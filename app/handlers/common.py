import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from app.config import ADMIN_ID, DEFAULT_LANGUAGE
from app.translations import t
from app.keyboards.inline import main_menu_keyboard, language_selection_keyboard
from app.database.queries import (
    get_user_by_telegram_id,
    upsert_user,
    update_user_language,
    get_latest_payment_and_enrollment,
    get_student_full_profile,
    get_course,
)

logger = logging.getLogger(__name__)


def get_user_lang(user_id: int) -> str:
    """Helper to retrieve user language or fallback to default."""
    user = get_user_by_telegram_id(user_id)
    if user and user.get("language"):
        return user["language"]
    return DEFAULT_LANGUAGE


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for /start command."""
    context.user_data.clear()
    user = update.effective_user

    # Upsert user record in MySQL
    db_user = upsert_user(
        telegram_id=user.id,
        full_name=user.full_name,
        username=user.username,
    )
    lang = db_user.get("language", DEFAULT_LANGUAGE) if db_user else DEFAULT_LANGUAGE

    welcome_text = t("welcome", lang)
    if update.message:
        await update.message.reply_text(
            welcome_text,
            reply_markup=main_menu_keyboard(lang),
            parse_mode="Markdown",
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            welcome_text,
            reply_markup=main_menu_keyboard(lang),
            parse_mode="Markdown",
        )
    return 0  # Represents CHOICE state in ConversationHandler


async def switch_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles language selection menu and updates."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "change_language":
        lang = get_user_lang(query.from_user.id)
        await query.edit_message_text(
            t("select_language", lang),
            reply_markup=language_selection_keyboard(),
            parse_mode="Markdown",
        )
        return 0

    if data.startswith("set_lang:"):
        selected_lang = data.split("set_lang:")[-1]
        update_user_language(query.from_user.id, selected_lang)
        confirm_text = t("language_set", selected_lang)
        await query.edit_message_text(
            f"{confirm_text}\n\n{t('welcome', selected_lang)}",
            reply_markup=main_menu_keyboard(selected_lang),
            parse_mode="Markdown",
        )
        return 0

    if data == "back_to_menu":
        lang = get_user_lang(query.from_user.id)
        await query.edit_message_text(
            t("welcome", lang),
            reply_markup=main_menu_keyboard(lang),
            parse_mode="Markdown",
        )
        return 0

    return 0


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays student's latest payment status and active enrollment."""
    user = update.effective_user
    lang = get_user_lang(user.id)
    record = get_latest_payment_and_enrollment(user.id)

    if not record:
        await update.message.reply_text(
            t("status_no_record", lang),
            parse_mode="Markdown",
        )
        return

    name = record.get("full_name") or user.full_name
    course_name = record.get("course_title") or "Freshman Course"
    payment_status = record.get("payment_status")
    enrollment_status = record.get("enrollment_status")

    if enrollment_status == "active" or payment_status == "approved":
        approved_time = record.get("approved_at") or record.get("payment_updated_at")
        text = (
            f"📊 *{t('status_title', lang)}*\n\n"
            f"👤 *Name:* {name}\n"
            f"📚 *Course:* {course_name}\n"
            f"🔖 *Status:* ✅ *APPROVED / ENROLLED*\n"
            f"🕒 *Approved Date:* {approved_time}\n"
        )
        if record.get("invite_link"):
            text += f"🔗 *Invite link:* {record.get('invite_link')}\n"
    elif payment_status == "pending":
        text = (
            f"📊 *{t('status_title', lang)}*\n\n"
            f"👤 *Name:* {name}\n"
            f"📚 *Course:* {course_name}\n"
            f"🧾 *Payment ID:* `#{record.get('payment_id')}`\n"
            f"🔖 *Status:* ⏳ *PENDING VERIFICATION*\n"
            f"🕒 *Submitted:* {record.get('payment_created_at')}\n"
            f"🔁 *Submissions:* {record.get('submission_count')}\n\n"
            f"The admin is verifying your transaction."
        )
    elif payment_status == "rejected":
        text = (
            f"📊 *{t('status_title', lang)}*\n\n"
            f"👤 *Name:* {name}\n"
            f"📚 *Course:* {course_name}\n"
            f"🧾 *Payment ID:* `#{record.get('payment_id')}`\n"
            f"🔖 *Status:* ❌ *REJECTED*\n"
            f"🕒 *Date:* {record.get('rejected_at') or record.get('payment_updated_at')}\n\n"
            f"Use /start to submit a valid screenshot."
        )
    else:
        text = t("status_no_record", lang)

    await update.message.reply_text(text, parse_mode="Markdown")


async def myinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays comprehensive profile info and payment history for student."""
    user = update.effective_user
    profile = get_student_full_profile(user.id)
    lang = get_user_lang(user.id)

    if not profile or not profile.get("user"):
        await update.message.reply_text(t("status_no_record", lang), parse_mode="Markdown")
        return

    u = profile["user"]
    enrollments = profile.get("enrollments", [])
    payments = profile.get("payments", [])

    text_parts = [
        f"📋 *{t('myinfo_title', lang)}*\n",
        f"👤 *Name:* {u.get('full_name')}",
        f"🆔 *Telegram ID:* `{u.get('telegram_id')}`",
        f"📱 *Username:* @{u.get('username') or 'N/A'}",
        f"🌐 *Language:* {u.get('language') or 'en'}",
        f"📅 *Registered:* {u.get('created_at')}",
    ]

    if enrollments:
        text_parts.append("\n🎓 *Active Enrollments:*")
        for e in enrollments:
            text_parts.append(
                f"• {e.get('course_title', 'Course')} (Enrolled: {e.get('enrolled_at')})"
            )

    if payments:
        text_parts.append("\n💳 *Payment Records:*")
        for p in payments:
            text_parts.append(
                f"• Payment `#{p.get('id')}` | Status: *{p.get('status').upper()}* | "
                f"Attempts: {p.get('submission_count')} | Date: {p.get('created_at')}"
            )

    await update.message.reply_text("\n".join(text_parts), parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays localized help message."""
    user = update.effective_user
    lang = get_user_lang(user.id)
    await update.message.reply_text(t("help_text", lang), parse_mode="Markdown")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels active conversation flow."""
    user = update.effective_user
    lang = get_user_lang(user.id)
    context.user_data.clear()
    await update.message.reply_text(
        t("cancel_success", lang),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def get_group_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Helper command to get chat ID and chat type."""
    chat = update.effective_chat
    await update.message.reply_text(
        f"Chat ID: `{chat.id}`\nChat type: `{chat.type}`",
        parse_mode="Markdown",
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler logging exceptions and informing admin safely."""
    logger.exception("Unhandled exception in Telegram bot: %s", context.error)
    if ADMIN_ID:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"⚠️ *Bot Error Report*\n\n`{str(context.error)[:300]}`",
                parse_mode="Markdown",
            )
        except Exception:
            pass
