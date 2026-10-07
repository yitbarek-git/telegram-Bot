import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Base directory of the project (portable across Windows, Linux, macOS)
BASE_DIR = Path(__file__).resolve().parent.parent

# Telegram Bot Credentials
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Admin IDs (comma-separated integers, e.g. "123456789,987654321")
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "").strip()
if not ADMIN_IDS_RAW:
    ADMIN_IDS_RAW = os.getenv("ADMIN_ID", "0").strip()

ADMIN_IDS = set()
for item in ADMIN_IDS_RAW.split(","):
    cleaned = item.strip()
    if cleaned:
        try:
            ADMIN_IDS.add(int(cleaned))
        except ValueError:
            pass

# Private Group ID for student access (numeric ID, e.g. -100xxxxxxxxxx)
PRIVATE_GROUP_ID_RAW = os.getenv("PRIVATE_GROUP_ID") or os.getenv("GROUP_ID", "0").strip()
try:
    PRIVATE_GROUP_ID = int(PRIVATE_GROUP_ID_RAW) if PRIVATE_GROUP_ID_RAW else 0
except ValueError:
    PRIVATE_GROUP_ID = 0

# Configured fallback link to the private group
FALLBACK_GROUP_LINK = os.getenv(
    "FALLBACK_GROUP_LINK", "https://t.me/+m6ikHXVS_ss0N2Vk"
).strip()

# HTTP Health Server Configuration (optional)
ENABLE_HEALTH_SERVER = os.getenv("ENABLE_HEALTH_SERVER", "true").strip().lower() in ("true", "1", "yes")
HOST = os.getenv("HOST", "0.0.0.0").strip()
PORT = int(os.getenv("PORT", "3000"))

# Portable Storage paths (relative to project root unless absolute path specified)
DATA_DIR_NAME = os.getenv("DATA_DIR", "data").strip()
if os.path.isabs(DATA_DIR_NAME):
    DATA_DIR = Path(DATA_DIR_NAME)
else:
    DATA_DIR = BASE_DIR / DATA_DIR_NAME

USERS_FILE = str(DATA_DIR / "users.json")
PAYMENTS_FILE = str(DATA_DIR / "payments.json")
DATA_DIR = str(DATA_DIR)

# A+ Academy Offer & Payment Account Details (Ethiopian focused)
DEFAULT_COURSE = "freshman"
DEFAULT_PRICE = os.getenv("COURSE_PRICE", "400 ETB").strip()

TELEBIRR_NUMBER = os.getenv("TELEBIRR_NUMBER", "0929781996").strip()
TELEBIRR_NAME = os.getenv("TELEBIRR_NAME", "A+ Academy / Amanuel").strip()

CBE_ACCOUNT = os.getenv("CBE_ACCOUNT", "1000316427735").strip()
CBE_NAME = os.getenv("CBE_NAME", "A+ Academy / Amanuel").strip()

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ["en", "am"]
