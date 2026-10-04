import os
import json
import unittest
import urllib.request
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock
from app.translations import t, TRANSLATIONS
from app.storage import (
    upsert_user,
    get_user_by_telegram_id,
    create_or_update_payment,
    get_payment_by_id,
    approve_payment,
    reject_payment,
    get_latest_payment_and_enrollment,
    get_student_full_profile,
    get_admin_stats,
    update_user_language,
    get_course,
)
from app.handlers.admin import generate_group_invite_link
from app.config import FALLBACK_GROUP_LINK
from app.web import start_web_server


class TestTranslations(unittest.TestCase):
    def test_translation_consistency(self):
        """Verify keys match across languages."""
        en_keys = set(TRANSLATIONS["en"].keys())
        am_keys = set(TRANSLATIONS["am"].keys())
        self.assertEqual(en_keys, am_keys, f"Mismatched keys: {en_keys ^ am_keys}")

    def test_translation_formatting(self):
        res = t("receipt_received_pending", "en", payment_id=101)
        self.assertIn("#101", res)
        res_am = t("receipt_received_pending", "am", payment_id=101)
        self.assertIn("#101", res_am)

    def test_unrelated_message_translation(self):
        res_en = t("unrelated_message", "en")
        res_am = t("unrelated_message", "am")
        self.assertIn("A+ Academy", res_en)
        self.assertIn("A+ Academy", res_am)


class TestInviteLinkGeneration(unittest.TestCase):
    def test_generate_invite_link_success_no_expiration_no_limit(self):
        """Verify invite is generated without expire_date or member_limit."""
        bot_mock = MagicMock()
        invite_result = MagicMock()
        invite_result.invite_link = "https://t.me/+generatedPermanentLink123"
        bot_mock.create_chat_invite_link = AsyncMock(return_value=invite_result)

        chat_id = -1001234567890
        link = asyncio.run(
            generate_group_invite_link(bot_mock, chat_id, payment_id=42, student_id=987654)
        )

        self.assertEqual(link, "https://t.me/+generatedPermanentLink123")
        # Ensure create_chat_invite_link was called with expire_date=None and member_limit=None
        bot_mock.create_chat_invite_link.assert_called_once_with(
            chat_id=chat_id,
            name="Student 987654 (Pay #42)",
            expire_date=None,
            member_limit=None,
            creates_join_request=False,
        )

    def test_generate_invite_link_fallback_on_error(self):
        """Verify fallback link is safely returned when Telegram returns an error."""
        bot_mock = MagicMock()
        bot_mock.create_chat_invite_link = AsyncMock(side_effect=Exception("Chat not found"))
        bot_mock.send_message = AsyncMock()

        chat_id = -1009999999999
        link = asyncio.run(
            generate_group_invite_link(bot_mock, chat_id, payment_id=43, student_id=987654)
        )

        self.assertEqual(link, FALLBACK_GROUP_LINK)

    def test_generate_invite_link_no_chat_id(self):
        """Verify fallback link is returned if chat_id is 0."""
        bot_mock = MagicMock()
        link = asyncio.run(
            generate_group_invite_link(bot_mock, 0, payment_id=44, student_id=987654)
        )
        self.assertEqual(link, FALLBACK_GROUP_LINK)


class TestJsonStorage(unittest.TestCase):
    def setUp(self):
        self.test_tg_id = int(time.time() * 1000) % 1000000000

    def test_course_information(self):
        course = get_course("freshman")
        self.assertEqual(course["price"], "400 ETB")
        self.assertIn("0929781996", course["telebirr_number"])
        self.assertIn("1000316427735", course["cbe_account"])

    def test_user_and_payment_flow(self):
        # 1. Upsert user
        user = upsert_user(
            telegram_id=self.test_tg_id,
            full_name="Dawit Bekele",
            username="dawit_b",
            language="am",
        )
        self.assertIsNotNone(user)
        self.assertEqual(user["full_name"], "Dawit Bekele")
        self.assertEqual(user["language"], "am")

        # 2. Update language
        update_user_language(self.test_tg_id, "en")
        user = get_user_by_telegram_id(self.test_tg_id)
        self.assertEqual(user["language"], "en")

        # 3. Create payment with payment method
        payment_id, is_update, count = create_or_update_payment(
            telegram_id=self.test_tg_id,
            file_type="photo",
            file_id="photo_file_id_12345",
            payment_method="Telebirr",
        )
        self.assertFalse(is_update)
        self.assertEqual(count, 1)

        # 4. Check payment
        payment = get_payment_by_id(payment_id)
        self.assertIsNotNone(payment)
        self.assertEqual(payment["status"], "pending")
        self.assertEqual(payment["payment_method"], "Telebirr")

        # 5. Check admin stats
        stats = get_admin_stats()
        self.assertGreaterEqual(stats["pending_payments"], 1)

        # 6. Approve payment
        approved = approve_payment(payment_id, "https://t.me/+m6ikHXVS_ss0N2Vk")
        self.assertEqual(approved["status"], "approved")

        # Verify duplicate approval prevention
        dup_approve = approve_payment(payment_id, "https://t.me/+m6ikHXVS_ss0N2Vk")
        self.assertIsNone(dup_approve)

        # 7. Check student profile & status
        status = get_latest_payment_and_enrollment(self.test_tg_id)
        self.assertEqual(status["payment_status"], "approved")
        self.assertEqual(status["enrollment_status"], "active")
        self.assertEqual(status["invite_link"], "https://t.me/+m6ikHXVS_ss0N2Vk")

        profile = get_student_full_profile(self.test_tg_id)
        self.assertIsNotNone(profile)
        self.assertEqual(len(profile["enrollments"]), 1)


class TestWebServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = start_web_server(port=3096)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_root_endpoint(self):
        req = urllib.request.urlopen("http://localhost:3096/")
        self.assertEqual(req.status, 200)
        self.assertEqual(req.read().decode("utf-8"), "A+ Academy Bot is running.")

    def test_health_endpoint(self):
        req = urllib.request.urlopen("http://localhost:3096/health")
        self.assertEqual(req.status, 200)
        body = json.loads(req.read().decode("utf-8"))
        self.assertEqual(body["status"], "healthy")
        self.assertEqual(body["storage"], "JSON")


if __name__ == "__main__":
    unittest.main()
