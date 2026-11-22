"""Offline regressions: never import application startup or connect to services.

Run: python -m unittest discover -s tests/offline -v
Only the automation class AST and the pure template module are evaluated.
"""

import ast
import asyncio
import os
from contextlib import redirect_stdout
from datetime import datetime
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]


def load_automation_class():
    source = ROOT / "complete_sequence_automation.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    definition = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    namespace = {"datetime": datetime, "asyncio": asyncio, "os": os}
    exec(compile(ast.Module(body=[definition], type_ignores=[]), str(source), "exec"), namespace)
    return namespace["CompleteSequenceAutomation"]


class StorageSpy:
    def __init__(self):
        self.lock_attempts = []
        self.unexpected_accesses = []
        self.db = SimpleNamespace(email_sequences=self)

    def find_one_and_update(self, query, update, **options):
        self.lock_attempts.append((query, update))
        return None  # Simulate another worker owning the record.

    def __getattr__(self, name):
        self.unexpected_accesses.append(name)
        raise AssertionError(f"Unexpected storage access: {name}")


class SequenceConfigurationTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"GFMD_EMAIL_SEND_ENABLED": "1"})
        self.env.start()
        automation_class = load_automation_class()
        self.worker = object.__new__(automation_class)  # Never run its constructor.
        template_source = ROOT / "email_sequence_templates.py"
        template_tree = ast.parse(template_source.read_text(encoding="utf-8"))
        template_nodes = [node for node in template_tree.body if isinstance(node, (ast.Import, ast.ImportFrom, ast.ClassDef))]
        namespace = {}
        exec(compile(ast.Module(body=template_nodes, type_ignores=[]), str(template_source), "exec"), namespace)
        self.worker.templates = namespace["EmailSequenceTemplates"]()
        self.worker.storage = StorageSpy()
        self.worker.gmail = SimpleNamespace(service=object())

    def tearDown(self):
        self.env.stop()
        self.assertEqual(self.worker.storage.unexpected_accesses, [])

    def sequence(self, **overrides):
        return {"contact_id": "offline-contact", "contact_email": "offline@example.invalid",
                "campaign": "spectrum", "sequence_name": "spectrum_snf_ltc",
                "status": "active", "current_step": 7, **overrides}

    async def test_unknown_sequence_is_rejected_before_lock_or_completion(self):
        result = await self.worker._process_single_sequence(self.sequence(sequence_name="missing_spectrum_variant"), send_emails=True)
        self.assertFalse(result["success"])
        self.assertIn("Unsupported sequence", result["error"])
        self.assertEqual(self.worker.storage.lock_attempts, [])

    async def test_unknown_campaign_cannot_fall_back_to_narc_gone(self):
        record = self.sequence(campaign="unknown")
        del record["sequence_name"]
        result = await self.worker._process_single_sequence(record)
        self.assertFalse(result["success"])
        self.assertEqual(self.worker.storage.lock_attempts, [])

    async def test_campaign_template_mismatch_is_rejected(self):
        result = await self.worker._process_single_sequence(self.sequence(sequence_name="narc_gone_law_enforcement"))
        self.assertFalse(result["success"])
        self.assertEqual(self.worker.storage.lock_attempts, [])

    async def test_missing_step_does_not_complete_a_known_sequence(self):
        result = await self.worker._process_single_sequence(self.sequence(
            campaign="narc_gone", sequence_name="narc_gone_law_enforcement", current_step=6))
        self.assertFalse(result["success"])
        self.assertIn("Missing template", result["error"])
        self.assertEqual(self.worker.storage.lock_attempts, [])

    async def test_supported_campaign_still_uses_atomic_lock(self):
        result = await self.worker._process_single_sequence(self.sequence(
            campaign="centrifuge", sequence_name="centrifuge_hospital_labs", current_step=0))
        self.assertEqual(result["reason"], "concurrent_processing")
        self.assertEqual(len(self.worker.storage.lock_attempts), 1)
        self.assertEqual(self.worker.storage.lock_attempts[0][0]["campaign"], "centrifuge")

    async def test_legacy_narc_record_still_uses_atomic_lock(self):
        record = self.sequence(current_step=0)
        del record["campaign"]
        del record["sequence_name"]
        result = await self.worker._process_single_sequence(record)
        self.assertEqual(result["reason"], "concurrent_processing")
        self.assertIsNone(self.worker.storage.lock_attempts[0][0]["campaign"])

    async def test_unsupported_enrollment_has_no_storage_access(self):
        result = self.worker.start_sequence_for_contact("offline-contact", campaign="unknown")
        self.assertFalse(result["success"])
        self.assertIn("Unsupported campaign", result["error"])
        result = await self.worker.add_daily_new_contacts(campaign="unknown")
        self.assertFalse(result["success"])
        self.assertIn("Unsupported campaign", result["error"])
        self.assertEqual(self.worker.storage.lock_attempts, [])


class SchedulerReportingTests(unittest.TestCase):
    def test_configuration_errors_are_not_reported_as_empty_queue(self):
        worker = object.__new__(load_automation_class())

        async def failed_processing(**kwargs):
            return {"processed": 1, "sent": 0, "errors": 1}

        worker.process_due_sequences = failed_processing
        output = StringIO()
        with redirect_stdout(output):
            worker._scheduled_processing()
        self.assertIn("Scheduled processing failed", output.getvalue())
        self.assertNotIn("No emails due", output.getvalue())


if __name__ == "__main__":
    unittest.main()
