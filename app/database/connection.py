import logging
import pymysql
import pymysql.cursors
from contextlib import contextmanager
from app.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

logger = logging.getLogger(__name__)

@contextmanager
def get_db():
    """
    Context manager that yields a PyMySQL connection with DictCursor.
    Ensures safe commit and cleanup.
    """
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        connect_timeout=10,
    )
    try:
        yield connection
    except Exception as e:
        logger.error(f"Database error occurred: {e}")
        try:
            connection.rollback()
        except Exception:
            pass
        raise
    finally:
        try:
            connection.close()
        except Exception:
            pass
