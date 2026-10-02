import sys
import unittest
from app.translations import t, TRANSLATIONS

class TestBotTranslations(unittest.TestCase):
    def test_translations_keys_consistency(self):
        """Verify that all keys in English exist in Amharic and format without crashing."""
        en_keys = set(TRANSLATIONS["en"].keys())
        am_keys = set(TRANSLATIONS["am"].keys())
        self.assertEqual(en_keys, am_keys, f"Missing keys: {en_keys ^ am_keys}")

    def test_translation_formatting(self):
        """Verify key string formatting works for placeholders."""
        res_en = t("received_first", "en", payment_id=42)
        self.assertIn("#42", res_en)

        res_am = t("received_first", "am", payment_id=42)
        self.assertIn("#42", res_am)

        course_str = t(
            "course_info",
            "en",
            title="Freshman",
            price="400 ETB",
            telebirr="0929781996",
            cbe="1000316427735",
            description="All subjects",
        )
        self.assertIn("Freshman", course_str)
        self.assertIn("0929781996", course_str)
        self.assertIn("1000316427735", course_str)

    def test_default_fallback(self):
        """Verify fallback to English if unknown language code provided."""
        res = t("btn_join_freshman", "unknown_lang")
        self.assertEqual(res, TRANSLATIONS["en"]["btn_join_freshman"])


class TestSqlSchema(unittest.TestCase):
    def test_schema_sql_syntax(self):
        """Verify sql/schema.sql has required tables and constraints."""
        with open("sql/schema.sql", "r", encoding="utf-8") as f:
            sql_content = f.read()
        self.assertIn("CREATE TABLE IF NOT EXISTS users", sql_content)
        self.assertIn("CREATE TABLE IF NOT EXISTS courses", sql_content)
        self.assertIn("CREATE TABLE IF NOT EXISTS payments", sql_content)
        self.assertIn("CREATE TABLE IF NOT EXISTS enrollments", sql_content)
        self.assertIn("telebirr_number", sql_content)
        self.assertIn("cbe_number", sql_content)
        self.assertIn("freshman", sql_content)


if __name__ == "__main__":
    unittest.main()
