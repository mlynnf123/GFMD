"""Release must not confuse a web heartbeat with a live scheduler."""
import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from unittest.mock import AsyncMock

import health_server
import production_readiness


class ReleaseReadinessTests(unittest.TestCase):
    def test_scheduler_exit_is_unhealthy_even_with_web_server_alive(self):
        with patch.object(health_server, "scheduler_process", SimpleNamespace(poll=lambda: 17)), \
             patch.dict(health_server.automation_status, {"status": "running"}, clear=True):
            response = health_server.app.test_client().get("/health")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json["automation"]["exit_code"], 17)
        self.assertEqual(response.json["automation"]["status"], "failed")

    def test_start_requires_explicit_automation_enablement(self):
        with patch.dict(os.environ, {"GFMD_AUTOMATION_ENABLED": "0"}), \
             patch.object(health_server.subprocess, "Popen", side_effect=AssertionError("No scheduler launch")), \
             patch.dict(health_server.automation_status, {"status": "starting"}, clear=True):
            health_server.start_scheduler()
            self.assertEqual(health_server.automation_status["status"], "disabled")

    def test_failed_integrations_block_an_enabled_scheduler(self):
        with patch.dict(os.environ, {"GFMD_AUTOMATION_ENABLED": "1"}), \
             patch.dict(health_server.integration_readiness, {"ready": False}, clear=True), \
             patch.dict(health_server.automation_status, {"status": "starting"}, clear=True), \
             patch.object(health_server.subprocess, "Popen", side_effect=AssertionError("No scheduler launch")):
            health_server.start_scheduler()
            self.assertEqual(health_server.automation_status["status"], "blocked")

    def test_readiness_fails_until_real_checks_pass(self):
        with patch.dict(health_server.integration_readiness, {"ready": False, "status": "checking"}, clear=True):
            self.assertEqual(health_server.app.test_client().get("/readiness").status_code, 503)

    def test_readiness_requires_verified_mailbox_and_does_no_database_writes(self):
        import gmail_integration
        import groq
        import pymongo
        import spectrum_ai
        profile = SimpleNamespace(execute=lambda: {"emailAddress": "wrong@example.invalid"})
        gmail = SimpleNamespace(service=SimpleNamespace(users=lambda: SimpleNamespace(getProfile=lambda **kwargs: profile)))
        client = SimpleNamespace(admin=SimpleNamespace(command=lambda _: None), close=lambda: None,
                                 gfmd_narc_gone=SimpleNamespace(email_sequences=SimpleNamespace(count_documents=lambda _: 0)))
        with patch.dict(os.environ, {"MONGODB_URI": "mongodb://example.invalid", "GFMD_EMAIL_SEND_ENABLED": "0"}), \
             patch.object(gmail_integration, "GmailIntegration", return_value=gmail), \
             patch.object(pymongo, "MongoClient", return_value=client), \
             patch.object(groq, "Groq", return_value=SimpleNamespace(close=lambda: None)), \
             patch.object(spectrum_ai, "generate_spectrum_draft", AsyncMock(return_value={"success": True, "ai_generated": True})):
            result = production_readiness.check_readiness()
        self.assertFalse(result["ready"])
        self.assertFalse(result["checks"]["gmail"]["ready"])
        self.assertTrue(result["checks"]["database"]["ready"])
