"""Real-module integration checks with in-memory MongoDB and fake Gmail transport.

Run only through the runtime validation runner, which blocks external connections
and runs in a temporary working directory without credentials or .env files.
"""

import asyncio
import base64
import copy
from datetime import datetime, timezone
from email import message_from_bytes
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

import mongomock
from bson import ObjectId

import ai_auto_reply_system
import complete_sequence_automation as automation
import email_reply_monitor
import gmail_integration
import groq_email_composer_agent
import health_server
import mongodb_storage
import spectrum_worker
from spectrum_campaign import SUBJECT, utc_datetime


NOW = datetime(2026, 8, 25, 15, 15, tzinfo=timezone.utc)


class FakeGmailTransport:
    """Records MIME locally; does not implement a network request."""

    def __init__(self):
        self.messages = {}
        self.timeout = False

    def users(self):
        return self

    def send(self, *, userId, body):
        def execute():
            number = len(self.messages) + 1
            message_id = f"fake-gmail-{number}"
            message = message_from_bytes(base64.urlsafe_b64decode(body['raw']))
            self.messages[message_id] = message
            if self.timeout:
                raise TimeoutError("Simulated ambiguous Gmail result")
            return {"id": message_id, "threadId": "fake-thread-1"}
        return SimpleNamespace(execute=execute)

    def get(self, *, userId, id, format, metadataHeaders):
        message = self.messages[id]
        return SimpleNamespace(execute=lambda: {
            "id": id, "threadId": "fake-thread-1",
            "payload": {"headers": [{"name": name, "value": message[name]} for name in metadataHeaders]},
        })


class RuntimeIntegrationTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mongo = mongomock.MongoClient()
        self.db = self.mongo.gfmd_python311_offline
        self.contact_id = ObjectId()
        self.sequence_id = ObjectId()
        self.db.contacts.insert_one({"_id": self.contact_id, "email": "alex@example.invalid", "campaign": "spectrum",
                                     "name": "Alex Example", "organization": "Example Care Facility", "status": "new"})
        self.db.email_sequences.insert_one({
            "_id": self.sequence_id, "contact_id": str(self.contact_id), "contact_email": "alex@example.invalid",
            "campaign": "spectrum", "sequence_name": "spectrum_snf_ltc", "current_step": 0,
            "status": "active", "emails_sent": [], "reply_received": False, "next_email_due": NOW.isoformat(),
        })
        self.storage = object.__new__(mongodb_storage.MongoDBStorage)
        self.storage.db, self.storage.contacts = self.db, self.db.contacts
        self.transport = FakeGmailTransport()
        # Gmail service uses users().messages(); keep the record dictionary separate.
        resource = SimpleNamespace(send=self.transport.send, get=self.transport.get)
        self.gmail = object.__new__(gmail_integration.GmailIntegration)
        self.gmail.service = SimpleNamespace(users=lambda: SimpleNamespace(messages=lambda: resource))
        self.reply_system = object.__new__(ai_auto_reply_system.AIAutoReplySystem)
        self.reply_system.storage, self.reply_system.gmail = self.storage, self.gmail
        self.reply_system.replied_message_ids = set()
        self.composer = object.__new__(groq_email_composer_agent.GroqEmailComposerAgent)
        from test_ai_restoration import fake_ai_client
        self.composer.client = fake_ai_client()
        self.reply_system.reply_agent = SimpleNamespace(client=fake_ai_client())
        with patch.object(automation, "MongoDBStorage", return_value=self.storage), \
             patch.object(automation, "GmailIntegration", return_value=self.gmail), \
             patch.object(automation, "GroqEmailComposerAgent", return_value=self.composer), \
             patch.object(ai_auto_reply_system, "AIAutoReplySystem", return_value=self.reply_system):
            self.worker = automation.CompleteSequenceAutomation()
        self.env = patch.dict("os.environ", {"GFMD_EMAIL_SEND_ENABLED": "1", "GFMD_SPECTRUM_SEND_ENABLED": "1", "GFMD_SPECTRUM_ENROLLMENT_ENABLED": "0"})
        self.env.start()
        self.monitor_patches = [
            patch.object(email_reply_monitor, "MongoDBStorage", return_value=self.storage),
            patch.object(email_reply_monitor, "GmailIntegration", return_value=self.gmail),
        ]
        for item in self.monitor_patches:
            item.start()

    def tearDown(self):
        for item in reversed(self.monitor_patches):
            item.stop()
        self.env.stop()

    def current(self):
        return self.db.email_sequences.find_one({"_id": self.sequence_id})

    async def process(self, now=NOW):
        real_processor = spectrum_worker.process_spectrum_sequence

        async def fixed_clock(worker, sequence, send_emails):
            return await real_processor(worker, sequence, send_emails, now=now)

        with patch.object(spectrum_worker, "process_spectrum_sequence", fixed_clock):
            return await self.worker._process_single_sequence(self.current())

    async def test_all_eight_steps_with_real_imports_bson_and_gmail_mime(self):
        now = NOW
        for step in range(1, 9):
            result = await self.process(now)
            self.assertTrue(result["success"], result)
            self.assertEqual(self.current()["current_step"], step)
            self.assertFalse(self.current()["processing"])
            if step < 8:
                now = utc_datetime(self.current()["next_email_due"])
        self.assertEqual(self.current()["status"], "completed")
        self.assertIsNone(self.current()["next_email_due"])
        self.assertEqual(len(self.transport.messages), 8)
        for step, message in enumerate(self.transport.messages.values(), 1):
            self.assertIn("@gfmd.com>", message["Message-ID"])
            if step > 1:
                parent = self.transport.messages[f"fake-gmail-{step-1}"]
                self.assertEqual(message["In-Reply-To"], parent["Message-ID"])
                self.assertEqual(message["References"], parent["Message-ID"])
        await self.process(now)
        self.assertEqual(len(self.transport.messages), 8)

    async def test_uncertain_send_is_held_with_real_storage_queries(self):
        self.transport.timeout = True
        self.assertEqual((await self.process())["action"], "needs_review")
        self.assertEqual(self.current()["current_step"], 0)
        self.assertEqual(self.current()["send_attempt"]["status"], "needs_review")
        await self.process()
        self.assertEqual(len(self.transport.messages), 1)

    async def test_ai_outage_leaves_step_unchanged_without_send_intent(self):
        self.composer.client = None
        result = await self.process()
        self.assertEqual(result["action"], "human_review")
        self.assertEqual(self.current()["current_step"], 0)
        self.assertNotIn("send_attempt", self.current())
        self.assertFalse(self.current()["processing"])
        self.assertEqual(len(self.transport.messages), 0)

    async def test_reply_draft_persists_once_across_repeated_processing(self):
        from test_ai_restoration import fake_ai_client
        calls = []
        self.reply_system.reply_agent.client = fake_ai_client(calls=calls)
        await self.process()
        reply = {"from_email": "alex@example.invalid", "message_id": "draft-repeat", "thread_id": "fake-thread-1",
                 "subject": "Re: " + SUBJECT, "content": "Please send pricing."}
        for _ in range(2):
            result = await self.reply_system.process_reply(reply)
            self.assertEqual(result["action"], "human_review")
        review = self.db.interactions.find_one({"original_message_id": "draft-repeat"})
        self.assertEqual(review["draft_status"], "ready")
        self.assertTrue(review["draft"]["ai_generated"])
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(self.transport.messages), 1)

    async def test_reply_during_generation_prevents_send(self):
        original = self.composer.execute
        async def change_state(task):
            result = await original(task)
            self.db.email_sequences.update_one({"_id": self.sequence_id}, {"$set": {"reply_received": True}})
            return result
        with patch.object(self.composer, "execute", change_state):
            result = await self.process()
        self.assertEqual(result["reason"], "state_changed_during_generation")
        self.assertNotIn("send_attempt", self.current())
        self.assertEqual(len(self.transport.messages), 0)

    async def test_recovered_campaign_reply_queues_once_when_sending_disabled(self):
        await self.process()
        self.db.email_sequences.update_one({"_id": self.sequence_id}, {"$set": {"campaign": "centrifuge"}})
        self.reply_system.reply_agent.execute = AsyncMock(return_value={"success": True, "subject": "Re: Product",
                                                                        "reply_body": "Draft for review"})
        reply = {"from_email": "alex@example.invalid", "message_id": "legacy-review", "thread_id": "fake-thread-1",
                 "subject": "Re: Product", "content": "Please send more information."}
        with patch.dict("os.environ", {"GFMD_EMAIL_SEND_ENABLED": "0"}):
            for _ in range(2):
                result = await self.reply_system.process_reply(reply)
                self.assertEqual(result["action"], "human_review")
        self.assertEqual(self.reply_system.reply_agent.execute.await_count, 1)
        self.assertEqual(self.db.interactions.count_documents({"type": "ai_reply_review"}), 1)
        self.assertEqual(self.current()["status"], "replied")
        self.assertEqual(len(self.transport.messages), 1)

    async def test_approved_spectrum_reply_sends_once_in_the_verified_thread(self):
        await self.process()
        reply = {"from_email": "alex@example.invalid", "message_id": "approved-incoming", "thread_id": "fake-thread-1",
                 "subject": "Re: " + SUBJECT, "content": "Please send information."}
        headers = {"success": True, "thread_id": "fake-thread-1", "rfc_message_id": "<incoming@example.invalid>", "subject": SUBJECT}
        with patch.dict("os.environ", {"GFMD_SPECTRUM_AUTO_REPLY_ENABLED": "1"}), \
             patch.object(self.gmail, "get_message_thread_headers", return_value=headers):
            first = await self.reply_system.process_reply(reply)
            again = await self.reply_system.process_reply(reply)
        self.assertTrue(first["actually_sent"])
        self.assertFalse(again["actually_sent"])
        self.assertEqual(len(self.transport.messages), 2)
        message = self.transport.messages['fake-gmail-2']
        self.assertEqual(message['In-Reply-To'], '<incoming@example.invalid>')
        self.assertEqual(self.db.interactions.find_one({"original_message_id": "approved-incoming"})["status"], "sent")

    async def test_approved_spectrum_reply_timeout_is_not_retried(self):
        await self.process()
        self.transport.timeout = True
        reply = {"from_email": "alex@example.invalid", "message_id": "ambiguous-reply", "thread_id": "fake-thread-1",
                 "subject": "Re: " + SUBJECT, "content": "Please send information."}
        headers = {"success": True, "thread_id": "fake-thread-1", "rfc_message_id": "<incoming@example.invalid>", "subject": SUBJECT}
        with patch.dict("os.environ", {"GFMD_SPECTRUM_AUTO_REPLY_ENABLED": "1"}), \
             patch.object(self.gmail, "get_message_thread_headers", return_value=headers):
            first = await self.reply_system.process_reply(reply)
            again = await self.reply_system.process_reply(reply)
        self.assertEqual(first['action'], 'needs_review')
        self.assertFalse(again['actually_sent'])
        self.assertEqual(len(self.transport.messages), 2)

    def test_failed_daily_scan_does_not_log_success(self):
        with patch.object(self.gmail, "get_emails", side_effect=gmail_integration.GmailReadError("Expired")):
            self.worker._scan_for_bounces()
        self.assertEqual(self.db.system_logs.count_documents({"type": "daily_email_scan"}), 0)

    def test_spectrum_monitor_ignores_quoted_optout_and_unmatched_threads(self):
        sequence = self.current()
        self.db.email_sequences.update_one({"_id": self.sequence_id}, {"$set": {
            "emails_sent": [{"actually_sent": True, "gmail_thread_id": "known-thread"}]}})
        inbox = [{"id": "new-pricing", "from": "alex@example.invalid", "thread_id": "known-thread",
                  "subject": "Re: Spectrum", "body": "Please send pricing.\n\n> Unsubscribe?"},
                 {"id": "wrong-thread", "from": "alex@example.invalid", "thread_id": "unrelated",
                  "subject": "Re: Something else", "body": "Unsubscribe"}]
        monitor = email_reply_monitor.EmailReplyMonitor(storage=self.storage, gmail=self.gmail)
        with patch.object(self.gmail, "get_emails", return_value=inbox):
            stats = monitor.process_gmail_replies()
        self.assertTrue(stats["success"])
        self.assertEqual(self.db.suppression_list.count_documents({}), 0)

    async def test_real_suppression_monitor_stops_spectrum_without_mail(self):
        await self.process()
        reply = {"from_email": "alex@example.invalid", "message_id": "incoming-optout", "thread_id": "fake-thread-1",
                 "subject": "Re: " + SUBJECT, "content": "Please unsubscribe me."}
        await self.reply_system.process_reply(reply)
        self.assertEqual(self.current()["status"], "suppressed")
        self.assertEqual(self.db.suppression_list.count_documents({"email": "alex@example.invalid", "status": "active"}), 1)
        self.assertEqual(len(self.transport.messages), 1)

    async def test_quoted_old_decline_does_not_suppress_pricing_request(self):
        await self.process()
        reply = {"from_email": "alex@example.invalid", "message_id": "incoming-pricing", "thread_id": "fake-thread-1",
                 "subject": "Re: " + SUBJECT,
                 "content": "Please send pricing.\n\nOn Tuesday, Meranda wrote:\n> Right person, wrong person, or not now?"}
        result = await self.reply_system.process_reply(reply)
        self.assertIsNotNone(result)
        self.assertEqual(result["action"], "human_review")
        self.assertEqual(self.db.suppression_list.count_documents({}), 0)
        self.assertEqual(self.current()["status"], "replied")
        self.assertEqual(len(self.transport.messages), 1)

    async def test_unmatched_spectrum_thread_cannot_suppress_contact(self):
        await self.process()
        reply = {"from_email": "alex@example.invalid", "message_id": "unmatched", "thread_id": "unrelated-thread",
                 "subject": "Re: " + SUBJECT, "content": "Unsubscribe."}
        await self.reply_system.process_reply(reply)
        self.assertEqual(self.db.suppression_list.count_documents({}), 0)
        self.assertEqual(self.current()["status"], "active")
        self.assertEqual(len(self.transport.messages), 1)

    async def test_html_quoted_history_does_not_suppress_pricing_request(self):
        await self.process()
        reply = {"from_email": "alex@example.invalid", "message_id": "html-pricing", "thread_id": "fake-thread-1",
                 "subject": "Re: " + SUBJECT,
                 "content": '<div>Please send pricing.</div><div class="gmail_quote">Wrong person or unsubscribe?</div>'}
        result = await self.reply_system.process_reply(reply)
        self.assertEqual(result["action"], "human_review")
        self.assertEqual(self.db.suppression_list.count_documents({}), 0)
        review = self.db.interactions.find_one({"original_message_id": "html-pricing"})
        self.assertEqual(review["original_content"], reply["content"])
        self.assertEqual(len(self.transport.messages), 1)

    async def test_temporary_absence_is_reviewed_without_permanent_suppression(self):
        await self.process()
        reply = {"from_email": "alex@example.invalid", "message_id": "temporary-absence", "thread_id": "fake-thread-1",
                 "subject": "Automatic reply: " + SUBJECT, "content": "I am out of office until Monday."}
        result = await self.reply_system.process_reply(reply)
        self.assertEqual(result["action"], "human_review")
        self.assertEqual(self.db.suppression_list.count_documents({}), 0)
        self.assertEqual(self.current()["status"], "replied")

    async def test_out_of_office_with_explicit_optout_still_suppresses(self):
        await self.process()
        reply = {"from_email": "alex@example.invalid", "message_id": "absence-optout", "thread_id": "fake-thread-1",
                 "subject": "Automatic reply: " + SUBJECT,
                 "content": "I am out of office. Please unsubscribe me."}
        await self.reply_system.process_reply(reply)
        self.assertEqual(self.current()["status"], "suppressed")
        self.assertEqual(self.db.suppression_list.count_documents({}), 1)

    def test_flask_health_route_import_does_not_start_scheduler(self):
        with patch.object(health_server, "start_scheduler", side_effect=AssertionError("Scheduler must not start")):
            response = health_server.app.test_client().get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['automation']['status'], 'starting')
