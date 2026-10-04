import os
import json
import logging
from datetime import datetime
from threading import Lock
from typing import Optional, Dict, Any, List, Tuple
from app.config import (
    DATA_DIR,
    USERS_FILE,
    PAYMENTS_FILE,
    DEFAULT_COURSE,
    DEFAULT_PRICE,
    TELEBIRR_NUMBER,
    TELEBIRR_NAME,
    CBE_ACCOUNT,
    CBE_NAME,
    DEFAULT_LANGUAGE,
)

logger = logging.getLogger(__name__)

_storage_lock = Lock()


def _ensure_storage() -> None:
    """Ensure data directory and required JSON files exist and are valid."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE) == 0:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)

    if not os.path.exists(PAYMENTS_FILE) or os.path.getsize(PAYMENTS_FILE) == 0:
        with open(PAYMENTS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)


def _read_json(filepath: str, default_val: Any) -> Any:
    """Safely read JSON file with error recovery."""
    _ensure_storage()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Could not read %s (resetting): %s", filepath, e)
        return default_val


def _write_json(filepath: str, data: Any) -> None:
    """Atomically and safely write JSON file."""
    _ensure_storage()
    temp_file = f"{filepath}.tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(temp_file, filepath)


# ==========================================
# Course Details (Freshman Offer)
# ==========================================
def get_course(course_id: str = DEFAULT_COURSE) -> Dict[str, Any]:
    """Returns the course information."""
    return {
        "id": "freshman",
        "title": "Freshman Courses (Mathematics, Physics, English, Logic, Psychology, Economics, Emerging Tech...)",
        "price": DEFAULT_PRICE,
        "telebirr_number": TELEBIRR_NUMBER,
        "telebirr_name": TELEBIRR_NAME,
        "cbe_account": CBE_ACCOUNT,
        "cbe_name": CBE_NAME,
        "description": "Video Lessons, Lecture PDFs, Past Midterm & Final Solved Exams, Department Preparation",
    }


# ==========================================
# User Functions
# ==========================================
def get_user_by_telegram_id(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve user record by Telegram ID."""
    with _storage_lock:
        users = _read_json(USERS_FILE, {})
        return users.get(str(telegram_id))


def upsert_user(
    telegram_id: int,
    full_name: str,
    username: Optional[str] = None,
    language: Optional[str] = None,
) -> Dict[str, Any]:
    """Insert or update user record."""
    with _storage_lock:
        users = _read_json(USERS_FILE, {})
        key = str(telegram_id)
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        if key in users:
            user = users[key]
            if full_name:
                user["full_name"] = full_name
            if username is not None:
                user["username"] = username
            if language is not None:
                user["language"] = language
            user["updated_at"] = now_str
        else:
            user = {
                "telegram_id": telegram_id,
                "full_name": full_name or "Student",
                "username": username or "",
                "language": language or DEFAULT_LANGUAGE,
                "created_at": now_str,
                "updated_at": now_str,
                "payment_status": "none",
                "access_status": "none",
                "invite_link": None,
                "enrolled_at": None,
            }
        users[key] = user
        _write_json(USERS_FILE, users)
        return user


def update_user_language(telegram_id: int, language: str) -> None:
    """Update language preference for user."""
    with _storage_lock:
        users = _read_json(USERS_FILE, {})
        key = str(telegram_id)
        if key in users:
            users[key]["language"] = language
            users[key]["updated_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            _write_json(USERS_FILE, users)


# ==========================================
# Payment Functions
# ==========================================
def create_or_update_payment(
    telegram_id: int,
    file_type: str,
    file_id: str,
    payment_method: str = "telebirr",
    amount: str = DEFAULT_PRICE,
    course_id: str = DEFAULT_COURSE,
    reference_id: str = "",
) -> Tuple[int, bool, int]:
    """
    Creates a new payment record or updates an existing pending payment.
    Returns: (payment_id, is_update, submission_count)
    """
    with _storage_lock:
        payments = _read_json(PAYMENTS_FILE, [])
        users = _read_json(USERS_FILE, {})
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Check for existing pending payment for this user
        pending_idx = None
        for i, p in enumerate(payments):
            if p["telegram_id"] == telegram_id and p["status"] == "pending":
                pending_idx = i
                break

        if pending_idx is not None:
            p = payments[pending_idx]
            p["file_type"] = file_type
            p["file_id"] = file_id
            p["payment_method"] = payment_method or p.get("payment_method", "telebirr")
            if reference_id:
                p["reference_id"] = reference_id
            p["submission_count"] = p.get("submission_count", 1) + 1
            p["updated_at"] = now_str
            payments[pending_idx] = p
            _write_json(PAYMENTS_FILE, payments)
            return p["id"], True, p["submission_count"]

        # Calculate new sequential payment ID
        max_id = max([p.get("id", 0) for p in payments], default=0)
        new_id = max_id + 1

        submission_count = (
            sum(1 for p in payments if p["telegram_id"] == telegram_id) + 1
        )

        new_payment = {
            "id": new_id,
            "telegram_id": telegram_id,
            "course_id": course_id,
            "amount": amount,
            "payment_method": payment_method,
            "file_type": file_type,
            "file_id": file_id,
            "reference_id": reference_id,
            "status": "pending",
            "submission_count": submission_count,
            "created_at": now_str,
            "updated_at": now_str,
            "approved_at": None,
            "rejected_at": None,
        }
        payments.append(new_payment)
        _write_json(PAYMENTS_FILE, payments)

        # Update user's payment status to pending
        key = str(telegram_id)
        if key in users:
            users[key]["payment_status"] = "pending"
            users[key]["updated_at"] = now_str
            _write_json(USERS_FILE, users)

        return new_id, False, submission_count


def get_payment_by_id(payment_id: int) -> Optional[Dict[str, Any]]:
    """Fetch payment record along with user and course information."""
    with _storage_lock:
        payments = _read_json(PAYMENTS_FILE, [])
        users = _read_json(USERS_FILE, {})

        for p in payments:
            if p.get("id") == payment_id:
                res = dict(p)
                res["payment_id"] = p["id"]
                u = users.get(str(p["telegram_id"]), {})
                res["full_name"] = u.get("full_name", "Student")
                res["username"] = u.get("username", "")
                res["language"] = u.get("language", DEFAULT_LANGUAGE)
                course = get_course(p.get("course_id", DEFAULT_COURSE))
                res["course_title"] = course["title"]
                res["course_price"] = course["price"]
                return res
        return None


def approve_payment(payment_id: int, invite_link: str) -> Optional[Dict[str, Any]]:
    """Approve a payment, record single-use invite link, and mark user access approved."""
    with _storage_lock:
        payments = _read_json(PAYMENTS_FILE, [])
        users = _read_json(USERS_FILE, {})
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        matched = None
        for p in payments:
            if p.get("id") == payment_id:
                # Prevent duplicate approval
                if p.get("status") == "approved":
                    return None
                p["status"] = "approved"
                p["approved_at"] = now_str
                p["updated_at"] = now_str
                p["invite_link"] = invite_link
                matched = p
                break

        if not matched:
            return None

        # Update user access and payment status
        key = str(matched["telegram_id"])
        if key in users:
            users[key]["payment_status"] = "approved"
            users[key]["access_status"] = "approved"
            users[key]["invite_link"] = invite_link
            users[key]["enrolled_at"] = now_str
            users[key]["updated_at"] = now_str
            _write_json(USERS_FILE, users)

        _write_json(PAYMENTS_FILE, payments)

        u = users.get(key, {})
        return {
            **matched,
            "full_name": u.get("full_name", "Student"),
            "username": u.get("username", ""),
            "language": u.get("language", DEFAULT_LANGUAGE),
        }


def reject_payment(payment_id: int) -> Optional[Dict[str, Any]]:
    """Reject a payment."""
    with _storage_lock:
        payments = _read_json(PAYMENTS_FILE, [])
        users = _read_json(USERS_FILE, {})
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        matched = None
        for p in payments:
            if p.get("id") == payment_id:
                p["status"] = "rejected"
                p["rejected_at"] = now_str
                p["updated_at"] = now_str
                matched = p
                break

        if not matched:
            return None

        # Update user's payment status
        key = str(matched["telegram_id"])
        if key in users:
            users[key]["payment_status"] = "rejected"
            users[key]["updated_at"] = now_str
            _write_json(USERS_FILE, users)

        _write_json(PAYMENTS_FILE, payments)

        u = users.get(key, {})
        return {
            **matched,
            "full_name": u.get("full_name", "Student"),
            "username": u.get("username", ""),
            "language": u.get("language", DEFAULT_LANGUAGE),
        }


def get_latest_payment_and_enrollment(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Fetch student's latest payment status and enrollment info."""
    with _storage_lock:
        payments = _read_json(PAYMENTS_FILE, [])
        users = _read_json(USERS_FILE, {})

        user = users.get(str(telegram_id))
        user_payments = [p for p in payments if p.get("telegram_id") == telegram_id]
        if not user_payments and not user:
            return None

        latest_payment = user_payments[-1] if user_payments else {}
        course = get_course(latest_payment.get("course_id", DEFAULT_COURSE))

        return {
            "telegram_id": telegram_id,
            "full_name": user.get("full_name") if user else "Student",
            "username": user.get("username") if user else "",
            "language": user.get("language", DEFAULT_LANGUAGE) if user else DEFAULT_LANGUAGE,
            "payment_id": latest_payment.get("id"),
            "payment_status": latest_payment.get("status") or (user.get("payment_status") if user else "none"),
            "payment_method": latest_payment.get("payment_method", "telebirr"),
            "submission_count": latest_payment.get("submission_count", 0),
            "payment_created_at": latest_payment.get("created_at"),
            "approved_at": latest_payment.get("approved_at"),
            "rejected_at": latest_payment.get("rejected_at"),
            "course_title": course["title"],
            "enrollment_status": "active" if user and user.get("access_status") == "approved" else "none",
            "enrolled_at": user.get("enrolled_at") if user else None,
            "invite_link": user.get("invite_link") if user else latest_payment.get("invite_link"),
        }


def get_student_full_profile(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Complete profile lookup for admin /student command."""
    with _storage_lock:
        payments = _read_json(PAYMENTS_FILE, [])
        users = _read_json(USERS_FILE, {})

        user = users.get(str(telegram_id))
        if not user:
            return None

        user_payments = [p for p in payments if p.get("telegram_id") == telegram_id]
        user_payments.sort(key=lambda x: x.get("id", 0), reverse=True)

        course = get_course(DEFAULT_COURSE)
        enrollments = []
        if user.get("access_status") == "approved":
            enrollments.append({
                "course_title": course["title"],
                "status": "active",
                "invite_link": user.get("invite_link"),
                "enrolled_at": user.get("enrolled_at") or user.get("updated_at"),
            })

        for p in user_payments:
            p["course_title"] = course["title"]

        return {
            "user": user,
            "enrollments": enrollments,
            "payments": user_payments,
        }


def get_admin_stats() -> Dict[str, Any]:
    """Retrieve statistical counters and pending submissions for admin."""
    with _storage_lock:
        payments = _read_json(PAYMENTS_FILE, [])
        users = _read_json(USERS_FILE, {})
        course = get_course(DEFAULT_COURSE)

        total_users = len(users)
        total_enrollments = sum(1 for u in users.values() if u.get("access_status") == "approved")
        pending_payments = sum(1 for p in payments if p.get("status") == "pending")
        approved_payments = sum(1 for p in payments if p.get("status") == "approved")
        rejected_payments = sum(1 for p in payments if p.get("status") == "rejected")

        pending_list = []
        for p in payments:
            if p.get("status") == "pending":
                u = users.get(str(p["telegram_id"]), {})
                pending_list.append({
                    "payment_id": p.get("id"),
                    "submission_count": p.get("submission_count", 1),
                    "created_at": p.get("created_at"),
                    "payment_method": p.get("payment_method", "telebirr"),
                    "full_name": u.get("full_name", "Student"),
                    "telegram_id": p["telegram_id"],
                    "course_title": course["title"],
                })

        return {
            "total_users": total_users,
            "total_enrollments": total_enrollments,
            "pending_payments": pending_payments,
            "approved_payments": approved_payments,
            "rejected_payments": rejected_payments,
            "pending_list": pending_list,
        }
