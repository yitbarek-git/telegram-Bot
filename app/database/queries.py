import logging
from typing import Optional, Dict, Any, List, Tuple
from app.database.connection import get_db

logger = logging.getLogger(__name__)


def get_user_by_telegram_id(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Fetch user record by Telegram ID."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE telegram_id = %s LIMIT 1",
                (telegram_id,)
            )
            return cursor.fetchone()


def upsert_user(
    telegram_id: int,
    full_name: str,
    username: Optional[str] = None,
    language: Optional[str] = None,
) -> Dict[str, Any]:
    """Insert or update user record."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            if language:
                cursor.execute(
                    """
                    INSERT INTO users (telegram_id, full_name, username, language)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        full_name = VALUES(full_name),
                        username = VALUES(username),
                        language = VALUES(language)
                    """,
                    (telegram_id, full_name, username, language),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO users (telegram_id, full_name, username)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        full_name = VALUES(full_name),
                        username = VALUES(username)
                    """,
                    (telegram_id, full_name, username),
                )
            cursor.execute(
                "SELECT * FROM users WHERE telegram_id = %s LIMIT 1",
                (telegram_id,)
            )
            return cursor.fetchone()


def update_user_language(telegram_id: int, language: str) -> None:
    """Update language preference for user."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET language = %s WHERE telegram_id = %s",
                (language, telegram_id),
            )


def get_course(course_id: str = "freshman") -> Optional[Dict[str, Any]]:
    """Fetch course details by course ID."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM courses WHERE id = %s LIMIT 1",
                (course_id,)
            )
            return cursor.fetchone()


def create_or_update_payment(
    user_id: int,
    course_id: str,
    file_type: str,
    file_id: str,
) -> Tuple[int, bool, int]:
    """
    Creates a new payment record or updates an existing pending payment.
    Returns: (payment_id, is_update, submission_count)
    """
    with get_db() as conn:
        with conn.cursor() as cursor:
            # Check for existing pending payment
            cursor.execute(
                """
                SELECT id, submission_count FROM payments
                WHERE user_id = %s AND course_id = %s AND status = 'pending'
                ORDER BY id DESC LIMIT 1
                """,
                (user_id, course_id),
            )
            pending = cursor.fetchone()

            if pending:
                payment_id = pending["id"]
                new_count = pending["submission_count"] + 1
                cursor.execute(
                    """
                    UPDATE payments
                    SET file_type = %s, file_id = %s, submission_count = %s, updated_at = NOW()
                    WHERE id = %s
                    """,
                    (file_type, file_id, new_count, payment_id),
                )
                return payment_id, True, new_count
            else:
                # Count total previous submissions
                cursor.execute(
                    "SELECT COUNT(*) AS total FROM payments WHERE user_id = %s AND course_id = %s",
                    (user_id, course_id),
                )
                res = cursor.fetchone()
                submission_count = (res["total"] + 1) if res else 1

                cursor.execute(
                    """
                    INSERT INTO payments (user_id, course_id, file_type, file_id, status, submission_count)
                    VALUES (%s, %s, %s, %s, 'pending', %s)
                    """,
                    (user_id, course_id, file_type, file_id, submission_count),
                )
                payment_id = cursor.lastrowid
                return payment_id, False, submission_count


def get_payment_by_id(payment_id: int) -> Optional[Dict[str, Any]]:
    """Fetch payment record along with user and course details."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    p.id AS payment_id,
                    p.user_id,
                    p.course_id,
                    p.file_type,
                    p.file_id,
                    p.status,
                    p.submission_count,
                    p.created_at,
                    p.updated_at,
                    p.approved_at,
                    p.rejected_at,
                    u.telegram_id,
                    u.full_name,
                    u.username,
                    u.language,
                    c.title AS course_title,
                    c.price AS course_price
                FROM payments p
                JOIN users u ON p.user_id = u.id
                JOIN courses c ON p.course_id = c.id
                WHERE p.id = %s
                LIMIT 1
                """,
                (payment_id,),
            )
            return cursor.fetchone()


def approve_payment(payment_id: int, invite_link: str) -> Optional[Dict[str, Any]]:
    """
    Approves a payment, records the single-use invite link, and creates active enrollment.
    Returns the updated payment dict.
    """
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT p.*, u.telegram_id, u.full_name, u.language
                FROM payments p
                JOIN users u ON p.user_id = u.id
                WHERE p.id = %s
                """,
                (payment_id,),
            )
            payment = cursor.fetchone()
            if not payment:
                return None

            # Mark payment approved
            cursor.execute(
                """
                UPDATE payments
                SET status = 'approved', approved_at = NOW(), updated_at = NOW()
                WHERE id = %s
                """,
                (payment_id,),
            )

            # Insert enrollment
            cursor.execute(
                """
                INSERT INTO enrollments (user_id, course_id, payment_id, status, invite_link, enrolled_at)
                VALUES (%s, %s, %s, 'active', %s, NOW())
                """,
                (payment["user_id"], payment["course_id"], payment_id, invite_link),
            )

            payment["status"] = "approved"
            payment["invite_link"] = invite_link
            return payment


def reject_payment(payment_id: int) -> Optional[Dict[str, Any]]:
    """Marks payment rejected."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT p.*, u.telegram_id, u.full_name, u.language
                FROM payments p
                JOIN users u ON p.user_id = u.id
                WHERE p.id = %s
                """,
                (payment_id,),
            )
            payment = cursor.fetchone()
            if not payment:
                return None

            cursor.execute(
                """
                UPDATE payments
                SET status = 'rejected', rejected_at = NOW(), updated_at = NOW()
                WHERE id = %s
                """,
                (payment_id,),
            )
            payment["status"] = "rejected"
            return payment


def get_latest_payment_and_enrollment(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Fetch student's latest payment status and active enrollment info."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    u.id AS user_id,
                    u.telegram_id,
                    u.full_name,
                    u.language,
                    p.id AS payment_id,
                    p.status AS payment_status,
                    p.submission_count,
                    p.created_at AS payment_created_at,
                    p.approved_at,
                    p.rejected_at,
                    p.updated_at AS payment_updated_at,
                    c.title AS course_title,
                    e.id AS enrollment_id,
                    e.status AS enrollment_status,
                    e.enrolled_at,
                    e.invite_link
                FROM users u
                LEFT JOIN payments p ON p.user_id = u.id
                LEFT JOIN courses c ON c.id = p.course_id
                LEFT JOIN enrollments e ON e.payment_id = p.id
                WHERE u.telegram_id = %s
                ORDER BY p.id DESC
                LIMIT 1
                """,
                (telegram_id,),
            )
            return cursor.fetchone()


def get_student_full_profile(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Complete profile lookup for admin /student command."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE telegram_id = %s LIMIT 1",
                (telegram_id,)
            )
            user = cursor.fetchone()
            if not user:
                return None

            # Get enrollments
            cursor.execute(
                """
                SELECT e.*, c.title AS course_title
                FROM enrollments e
                JOIN courses c ON e.course_id = c.id
                WHERE e.user_id = %s
                ORDER BY e.enrolled_at DESC
                """,
                (user["id"],),
            )
            enrollments = cursor.fetchall()

            # Get all payments
            cursor.execute(
                """
                SELECT p.*, c.title AS course_title
                FROM payments p
                JOIN courses c ON p.course_id = c.id
                WHERE p.user_id = %s
                ORDER BY p.id DESC
                """,
                (user["id"],),
            )
            payments = cursor.fetchall()

            return {
                "user": user,
                "enrollments": enrollments,
                "payments": payments,
            }


def get_admin_stats() -> Dict[str, Any]:
    """Retrieve statistical counters and pending submissions for admin."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total_users FROM users")
            total_users = cursor.fetchone()["total_users"]

            cursor.execute("SELECT COUNT(*) AS total_enrollments FROM enrollments WHERE status = 'active'")
            total_enrollments = cursor.fetchone()["total_enrollments"]

            cursor.execute("SELECT COUNT(*) AS pending_payments FROM payments WHERE status = 'pending'")
            pending_payments = cursor.fetchone()["pending_payments"]

            cursor.execute("SELECT COUNT(*) AS approved_payments FROM payments WHERE status = 'approved'")
            approved_payments = cursor.fetchone()["approved_payments"]

            cursor.execute("SELECT COUNT(*) AS rejected_payments FROM payments WHERE status = 'rejected'")
            rejected_payments = cursor.fetchone()["rejected_payments"]

            cursor.execute(
                """
                SELECT 
                    p.id AS payment_id,
                    p.submission_count,
                    p.created_at,
                    u.full_name,
                    u.telegram_id,
                    c.title AS course_title
                FROM payments p
                JOIN users u ON p.user_id = u.id
                JOIN courses c ON p.course_id = c.id
                WHERE p.status = 'pending'
                ORDER BY p.id ASC
                LIMIT 20
                """
            )
            pending_list = cursor.fetchall()

            return {
                "total_users": total_users,
                "total_enrollments": total_enrollments,
                "pending_payments": pending_payments,
                "approved_payments": approved_payments,
                "rejected_payments": rejected_payments,
                "pending_list": pending_list,
            }
