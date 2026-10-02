import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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

# MySQL Database Configuration (Supports Aiven MySQL, AWS RDS, local, etc.)
# Supports both MYSQL_* and DB_* environment variable conventions
MYSQL_HOST = os.getenv("MYSQL_HOST") or os.getenv("DB_HOST", "localhost").strip()
_port_raw = os.getenv("MYSQL_PORT") or os.getenv("DB_PORT", "3306")
try:
    MYSQL_PORT = int(_port_raw) if _port_raw else 3306
except ValueError:
    MYSQL_PORT = 3306

MYSQL_USER = os.getenv("MYSQL_USER") or os.getenv("DB_USER", "avnadmin").strip()
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD") or os.getenv("DB_PASSWORD", "").strip()
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE") or os.getenv("DB_NAME", "defaultdb").strip()

# SSL Mode Configuration (Aiven MySQL requires SSL; default is 'REQUIRED')
# Options: 'REQUIRED', 'DISABLED', or path to CA cert pem file
MYSQL_SSL_MODE = os.getenv("MYSQL_SSL_MODE", "REQUIRED").strip()
MYSQL_SSL_CA = os.getenv("MYSQL_SSL_CA", "").strip()

# Bot Constants
DEFAULT_COURSE = "freshman"
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ["en", "am"]
