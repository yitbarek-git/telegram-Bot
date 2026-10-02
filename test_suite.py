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

    def test_default_fallback(self):
        """Verify fallback to English if unknown language code provided."""
        res = t("btn_join_freshman", "unknown_lang")
        self.assertEqual(res, TRANSLATIONS["en"]["btn_join_freshman"])


class TestSqlSchema(unittest.TestCase):
    def test_schema_syntax_and_tables(self):
        with open("sql/schema.sql", "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("CREATE TABLE IF NOT EXISTS users", content)
        self.assertIn("CREATE TABLE IF NOT EXISTS courses", content)
        self.assertIn("CREATE TABLE IF NOT EXISTS payments", content)
        self.assertIn("CREATE TABLE IF NOT EXISTS enrollments", content)
        self.assertIn("telebirr_number", content)
        self.assertIn("cbe_number", content)


if __name__ == "__main__":
    unittest.main()
