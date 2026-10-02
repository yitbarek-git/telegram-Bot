#!/usr/bin/env python3
"""
Migration script to migrate legacy users.json data into MySQL / Aiven database.
"""

import os
import json
import logging
from app.database.connection import get_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("migration")

JSON_FILE = "users.json"


def migrate():
    if not os.path.exists(JSON_FILE):
        logger.warning("File '%s' not found. Nothing to migrate.", JSON_FILE)
        return

    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.error("Failed to read '%s': %s", JSON_FILE, e)
        return

    logger.info("Loaded %d user records from '%s'. Starting MySQL migration...", len(data), JSON_FILE)

    migrated_users = 0
    migrated_payments = 0
    migrated_enrollments = 0

    with get_db() as conn:
        with conn.cursor() as cursor:
            for tg_id_str, u in data.items():
                try:
                    telegram_id = int(tg_id_str)
                except ValueError:
                    logger.warning("Skipping invalid Telegram ID key: %s", tg_id_str)
                    continue

                full_name = u.get("name") or "Student"
                username = u.get("username", "")
                if username and username.startswith("@"):
                    username = username[1:]

                # 1. Upsert User
                cursor.execute(
                    """
                    INSERT INTO users (telegram_id, full_name, username, language)
                    VALUES (%s, %s, %s, 'en')
                    ON DUPLICATE KEY UPDATE
                        full_name = VALUES(full_name),
                        username = VALUES(username)
                    """,
                    (telegram_id, full_name, username),
                )
                cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
                user_row = cursor.fetchone()
                user_id = user_row["id"]
                migrated_users += 1

                # 2. Insert Payment Record
                course_id = u.get("course", "freshman")
                file_type = u.get("file_type", "photo")
                file_id = u.get("file_id", "migrated_file_id")
                status = u.get("status", "pending")
                if status not in {"pending", "approved", "rejected"}:
                    status = "pending"
                submission_count = u.get("submission_count", 1)

                created_at = u.get("date") or u.get("updated_at")
                approved_at = u.get("approved_at") if status == "approved" else None
                rejected_at = u.get("rejected_at") if status == "rejected" else None

                cursor.execute(
                    """
                    INSERT INTO payments (user_id, course_id, file_type, file_id, status, submission_count, approved_at, rejected_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        user_id,
                        course_id,
                        file_type,
                        file_id,
                        status,
                        submission_count,
                        approved_at,
                        rejected_at,
                    ),
                )
                payment_id = cursor.lastrowid
                migrated_payments += 1

                # 3. Insert Enrollment if Approved
                if status == "approved":
                    cursor.execute(
                        """
                        INSERT INTO enrollments (user_id, course_id, payment_id, status, enrolled_at)
                        VALUES (%s, %s, %s, 'active', COALESCE(%s, NOW()))
                        """,
                        (user_id, course_id, payment_id, approved_at),
                    )
                    migrated_enrollments += 1

    logger.info("==========================================")
    logger.info(" Migration Completed Successfully! 🎉")
    logger.info(" Users Migrated:       %d", migrated_users)
    logger.info(" Payments Migrated:    %d", migrated_payments)
    logger.info(" Enrollments Created:  %d", migrated_enrollments)
    logger.info("==========================================")


if __name__ == "__main__":
    migrate()
