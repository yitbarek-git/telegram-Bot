import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from app.config import ADMIN_IDS, DEFAULT_LANGUAGE
from app.translations import t
from app.keyboards.inline import (
    main_menu_keyboard,
    language_selection_keyboard,
    payment_methods_keyboard,
)
from app.storage import (
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

    # Upsert user record in JSON
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
            parse_mode=None,
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            welcome_text,
            reply_markup=main_menu_keyboard(lang),
            parse_mode=None,
        )
    return ConversationHandler.END


async def my_enrollment_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays student enrollment status and access link."""
    user = update.effective_user
    lang = get_user_lang(user.id)
    record = get_latest_payment_and_enrollment(user.id)

    if not record or (record.get("payment_status") == "none" and record.get("enrollment_status") == "none"):
        if lang == "am":
            no_rec_text = (
                "📭 እስካሁን የተመዘገበ መረጃ አልተገኘም።\n\n"
                "በፍሬሽማን ኮርሶች ለመመዝገብ ከታች 'ክፍያ / ምዝገባ' የሚለውን ይጫኑ።"
            )
        else:
            no_rec_text = (
                "📭 No active enrollment or payment found.\n\n"
                "Please tap 'Payment / Enrollment' below to enroll in Freshman courses."
            )
        if update.callback_query:
            await update.callback_query.edit_message_text(
                no_rec_text,
                reply_markup=main_menu_keyboard(lang),
                parse_mode=None,
            )
        else:
            await update.message.reply_text(
                no_rec_text,
                reply_markup=main_menu_keyboard(lang),
                parse_mode=None,
            )
        return

    name = record.get("full_name") or user.full_name
    course_name = "Freshman Complete Package"
    payment_status = record.get("payment_status")
    enrollment_status = record.get("enrollment_status")

    if enrollment_status == "active" or payment_status == "approved":
        approved_time = record.get("approved_at") or record.get("payment_created_at") or ""
        link = record.get("invite_link") or "https://t.me/+m6ikHXVS_ss0N2Vk"
        if lang == "am":
            text = (
                "🎓 የእርስዎ ምዝገባ ተረጋግጧል (Active)\n\n"
                f"👤 ስም፦ {name}\n"
                f"📚 ኮርስ፦ {course_name}\n"
                f"🔖 ሁኔታ፦ ተረጋግጧል (Approved)\n"
                f"🕒 የተረጋገጠበት ቀን፦ {approved_time}\n\n"
                f"🔗 የፕራይቬት ግሩፕ ሊንክዎ፦\n{link}\n\n"
                "ሊንኩን ተጭነው የቪዲዮ ትምህርቶችንና የፈተና ጥያቄዎችን ያግኙ።"
            )
        else:
            text = (
                "🎓 Your Enrollment is Active\n\n"
                f"👤 Student: {name}\n"
                f"📚 Course: {course_name}\n"
                f"🔖 Status: Approved & Enrolled\n"
                f"🕒 Approved: {approved_time}\n\n"
                f"🔗 Your Private Group Link:\n{link}\n\n"
                "Click the link above to access all course videos and materials."
            )
    elif payment_status == "pending":
        if lang == "am":
            text = (
                "⏳ የክፍያ ደረሰኝዎ በማረጋገጥ ላይ ይገኛል\n\n"
                f"👤 ስም፦ {name}\n"
                f"📚 ኮርስ፦ {course_name}\n"
                f"🧾 የደረሰኝ መለያ፦ #{record.get('payment_id')}\n"
                f"🕒 የተላከበት ቀን፦ {record.get('payment_created_at')}\n"
                f"🔁 የሙከራ ብዛት፦ {record.get('submission_count', 1)}\n\n"
                "አስተዳዳሪው ደረሰኝዎን ሲያረጋግጥ የፕራይቬት ግሩፑ ሊንክ ወዲያውኑ ይደርስዎታል።"
            )
        else:
            text = (
                "⏳ Payment Pending Verification\n\n"
                f"👤 Student: {name}\n"
                f"📚 Course: {course_name}\n"
                f"🧾 Receipt ID: #{record.get('payment_id')}\n"
                f"🕒 Submitted: {record.get('payment_created_at')}\n"
                f"🔁 Submissions: {record.get('submission_count', 1)}\n\n"
                "Our team is reviewing your receipt. Your private group link will arrive once approved."
            )
    elif payment_status == "rejected":
        if lang == "am":
            text = (
                "❌ የክፍያ ደረሰኝዎ አልተረጋገጠም\n\n"
                f"👤 ስም፦ {name}\n"
                f"🧾 የደረሰኝ መለያ፦ #{record.get('payment_id')}\n"
                f"🔖 ሁኔታ፦ ውድቅ ተደርጓል (Rejected)\n\n"
                "እባክዎ ትክክለኛውን የ400 ብር የክፍያ Screenshot በድጋሚ ይላኩ።"
            )
        else:
            text = (
                "❌ Payment Not Approved\n\n"
                f"👤 Student: {name}\n"
                f"🧾 Receipt ID: #{record.get('payment_id')}\n"
                f"🔖 Status: Rejected\n\n"
                "Please submit a valid payment screenshot showing the 400 ETB transfer."
            )
    else:
        text = t("welcome", lang)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=main_menu_keyboard(lang),
            parse_mode=None,
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=main_menu_keyboard(lang),
            parse_mode=None,
        )


async def switch_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles language selection menu and updates."""
    query = update.callback_query
    if not query:
        return ConversationHandler.END

    await query.answer()
    data = query.data or ""

    if data == "change_language":
        lang = get_user_lang(query.from_user.id)
        await query.edit_message_text(
            t("select_language", lang),
            reply_markup=language_selection_keyboard(),
            parse_mode=None,
        )
        return ConversationHandler.END

    if data.startswith("set_lang:"):
        selected_lang = data.split("set_lang:")[-1]
        update_user_language(query.from_user.id, selected_lang)
        confirm_text = t("language_set", selected_lang)
        await query.edit_message_text(
            f"{confirm_text}\n\n{t('welcome', selected_lang)}",
            reply_markup=main_menu_keyboard(selected_lang),
            parse_mode=None,
        )
        return ConversationHandler.END

    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays localized help message in plain text."""
    user = update.effective_user
    lang = get_user_lang(user.id)
    await update.message.reply_text(
        t("help_text", lang),
        reply_markup=main_menu_keyboard(lang),
        parse_mode=None,
    )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels active conversation flow."""
    user = update.effective_user
    lang = get_user_lang(user.id)
    context.user_data.clear()
    await update.message.reply_text(
        t("cancel_success", lang),
        reply_markup=main_menu_keyboard(lang),
        parse_mode=None,
    )
    return ConversationHandler.END


async def get_group_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Helper command to get chat ID and chat type."""
    chat = update.effective_chat
    await update.message.reply_text(
        f"Chat ID: {chat.id}\nChat type: {chat.type}",
        parse_mode=None,
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler logging exceptions and safely informing admin."""
    logger.exception("Unhandled exception in Telegram bot: %s", context.error)
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"⚠️ Bot Exception: {str(context.error)[:300]}",
                parse_mode=None,
            )
        except Exception:
            pass
