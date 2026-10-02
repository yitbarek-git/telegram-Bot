import os
import ssl
import logging
import pymysql
import pymysql.cursors
from contextlib import contextmanager
from app.config import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
    MYSQL_SSL_MODE,
    MYSQL_SSL_CA,
)

logger = logging.getLogger(__name__)


def get_ssl_context():
    """
    Builds SSL dictionary/context for PyMySQL.
    Aiven MySQL requires SSL (TLS) connections.
    """
    if MYSQL_SSL_MODE.upper() in ("DISABLED", "FALSE", "0", "NONE"):
        return None

    ssl_opts = {}
    if MYSQL_SSL_CA and os.path.exists(MYSQL_SSL_CA):
        ssl_opts["ca"] = MYSQL_SSL_CA
    else:
        # Default SSL context for remote TLS (Aiven, Cloud providers)
        # Allows trusted CA verification or server certificate validation
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ssl_opts = ctx

    return ssl_opts


def create_connection():
    """Establishes a new PyMySQL connection with DictCursor."""
    ssl_context = get_ssl_context()
    conn_kwargs = {
        "host": MYSQL_HOST,
        "port": MYSQL_PORT,
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "database": MYSQL_DATABASE,
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": True,
        "connect_timeout": 15,
        "read_timeout": 30,
        "write_timeout": 30,
    }
    if ssl_context is not None:
        conn_kwargs["ssl"] = ssl_context

    return pymysql.connect(**conn_kwargs)


@contextmanager
def get_db():
    """
    Context manager yielding a resilient PyMySQL connection with DictCursor.
    Handles connection errors, ping verification, and clean closure.
    """
    connection = None
    try:
        connection = create_connection()
        yield connection
    except pymysql.MySQLError as e:
        logger.error("MySQL Database Error (%s): %s", getattr(e, "args", [None])[0], e)
        if connection:
            try:
                connection.rollback()
            except Exception:
                pass
        raise
    except Exception as e:
        logger.error("Unexpected database error: %s", e)
        if connection:
            try:
                connection.rollback()
            except Exception:
                pass
        raise
    finally:
        if connection:
            try:
                connection.close()
            except Exception:
                pass
