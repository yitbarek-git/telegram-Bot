import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID_RAW = os.getenv("ADMIN_ID", "0").strip()
GROUP_ID_RAW = os.getenv("GROUP_ID", "0").strip()

try:
    ADMIN_ID = int(ADMIN_ID_RAW) if ADMIN_ID_RAW else 0
except ValueError:
    ADMIN_ID = 0

try:
    GROUP_ID = int(GROUP_ID_RAW) if GROUP_ID_RAW else 0
except ValueError:
    GROUP_ID = 0

# Database Configuration (MySQL)
DB_HOST = os.getenv("DB_HOST", "localhost").strip()
DB_PORT = int(os.getenv("DB_PORT", "3306").strip() or 3306)
DB_USER = os.getenv("DB_USER", "root").strip()
DB_PASSWORD = os.getenv("DB_PASSWORD", "").strip()
DB_NAME = os.getenv("DB_NAME", "aplus_academy").strip()

# Webhook Configuration (Vercel)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").strip()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").strip()

# Bot Constants
DEFAULT_COURSE = "freshman"
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ["en", "am"]
