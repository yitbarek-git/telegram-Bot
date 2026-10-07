import logging
from app.config import ADMIN_IDS, DEFAULT_LANGUAGE
from app.translations import t
from app.keyboards.inline import (
    main_menu_keyboard,
    language_prompt_keyboard,
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
    """Helper to retrieve user language or fallback to default ('en')."""
    user = get_user_by_telegram_id(user_id)
    if user and user.get("language"):
        return user["language"]
    return DEFAULT_LANGUAGE


async def start(update, context) -> int:
    """
    Entry point for /start command.
    Presents language selection (🇬🇧 English / 🇪🇹 አማርኛ).
    """
    context.user_data.clear()
    user = update.effective_user

    # Upsert user record in JSON (preserves existing language if already set)
    db_user = upsert_user(
        telegram_id=user.id,
        full_name=user.full_name,
        username=user.username,
    )

    prompt_text = (
        "🎓 A+ Academy\n\n"
        "Choose your language / ቋንቋ ይምረጡ፦"
    )

    if update.message:
        await update.message.reply_text(
            prompt_text,
            reply_markup=language_prompt_keyboard(),
            parse_mode=None,
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            prompt_text,
            reply_markup=language_prompt_keyboard(),
            parse_mode=None,
        )
    return 0


async def my_enrollment_command(update, context) -> None:
    """Displays student enrollment status and access link."""
    user = update.effective_user
    lang = get_user_lang(user.id)
    record = get_latest_payment_and_enrollment(user.id)

    if not record or (record.get("payment_status") == "none" and record.get("enrollment_status") == "none"):
        if lang == "am":
            no_rec_text = (
                "👤 የእኔ ምዝገባ\n\n"
                "እስካሁን ምንም ንቁ ምዝገባ አልተገኘም።\n\n"
                "በፍሬሽማን ኮርሶች ለመመዝገብ ከታች 'ክፍያ / ምዝገባ' የሚለውን ይጫኑ።"
            )
        else:
            no_rec_text = (
                "👤 My Enrollment\n\n"
                "No active enrollment found.\n\n"
                "Please choose 'Payment / Enrollment' below to enroll in Freshman courses."
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
                "✅ ምዝገባዎ ንቁ ነው (Active)\n\n"
                f"ተማሪ፦ {name}\n"
                f"ኮርስ፦ {course_name}\n"
                f"ሁኔታ፦ ተረጋግጧል (Approved)\n"
                f"ቀን፦ {approved_time}\n\n"
                f"የፕራይቬት ግሩፕ ሊንክ፦\n{link}\n\n"
                "ትምህርቱን ለመጀመር ሊንኩን ተጭነው ግሩፑን ይቀላቀሉ።"
            )
        else:
            text = (
                "✅ Active Enrollment\n\n"
                f"Student: {name}\n"
                f"Course: {course_name}\n"
                f"Status: Approved\n"
                f"Date: {approved_time}\n\n"
                f"Private Group Link:\n{link}\n\n"
                "Click the link above to access all course materials."
            )
    elif payment_status == "pending":
        if lang == "am":
            text = (
                "⏳ በማረጋገጥ ላይ (Pending)\n\n"
                f"ተማሪ፦ {name}\n"
                f"ኮርስ፦ {course_name}\n"
                f"የደረሰኝ መለያ፦ #{record.get('payment_id')}\n"
                f"ቀን፦ {record.get('payment_created_at')}\n\n"
                "አስተዳዳሪው ደረሰኝዎን በማረጋገጥ ላይ ነው። እንደተረጋገጠ ሊንኩ ይላክልዎታል።"
            )
        else:
            text = (
                "⏳ Pending Verification\n\n"
                f"Student: {name}\n"
                f"Course: {course_name}\n"
                f"Receipt ID: #{record.get('payment_id')}\n"
                f"Date: {record.get('payment_created_at')}\n\n"
                "Your receipt is being reviewed. Your invite link will arrive once approved."
            )
    elif payment_status == "rejected":
        if lang == "am":
            text = (
                "❌ አልተረጋገጠም (Rejected)\n\n"
                f"ተማሪ፦ {name}\n"
                f"የደረሰኝ መለያ፦ #{record.get('payment_id')}\n\n"
                "የላኩት ደረሰኝ አልተረጋገጠም። እባክዎ ትክክለኛውን የ400 ETB ደረሰኝ በድጋሚ ይላኩ።"
            )
        else:
            text = (
                "❌ Payment Not Approved\n\n"
                f"Student: {name}\n"
                f"Receipt ID: #{record.get('payment_id')}\n\n"
                "Your receipt was not approved. Please submit a valid 400 ETB payment screenshot."
            )
    else:
        text = t("welcome", lang=lang)

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


async def switch_language_callback(update, context) -> int:
    """Handles initial selection from /start as well as language switcher menu."""
    query = update.callback_query
    if not query:
        return 0

    await query.answer()
    data = query.data or ""

    # User clicks 'Language' in menu
    if data == "change_language":
        lang = get_user_lang(query.from_user.id)
        await query.edit_message_text(
            t("select_language", lang=lang),
            reply_markup=language_selection_keyboard(),
            parse_mode=None,
        )
        return 0

    # User selected language from /start prompt
    if data.startswith("start_lang:"):
        selected_lang = data.split("start_lang:")[-1]
        update_user_language(query.from_user.id, selected_lang)
        welcome_text = t("welcome", lang=selected_lang)
        await query.edit_message_text(
            welcome_text,
            reply_markup=main_menu_keyboard(selected_lang),
            parse_mode=None,
        )
        return 0

    # User switched language from Settings
    if data.startswith("set_lang:"):
        selected_lang = data.split("set_lang:")[-1]
        update_user_language(query.from_user.id, selected_lang)
        confirm_text = t("language_set", lang=selected_lang)
        welcome_text = t("welcome", lang=selected_lang)
        await query.edit_message_text(
            f"{confirm_text}\n\n{welcome_text}",
            reply_markup=main_menu_keyboard(selected_lang),
            parse_mode=None,
        )
        return 0

    return 0


async def help_command(update, context) -> None:
    """Displays localized help message in plain text."""
    user = update.effective_user
    lang = get_user_lang(user.id)
    await update.message.reply_text(
        t("help_text", lang=lang),
        reply_markup=main_menu_keyboard(lang),
        parse_mode=None,
    )


async def cancel_command(update, context) -> int:
    """Cancels active conversation flow."""
    user = update.effective_user
    lang = get_user_lang(user.id)
    context.user_data.clear()
    await update.message.reply_text(
        t("cancel_success", lang=lang),
        reply_markup=main_menu_keyboard(lang),
        parse_mode=None,
    )
    return 0


async def get_group_id_command(update, context) -> None:
    """Helper command to get chat ID and chat type."""
    chat = update.effective_chat
    await update.message.reply_text(
        f"Chat ID: {chat.id}\nChat type: {chat.type}",
        parse_mode=None,
    )


async def error_handler(update: object, context) -> None:
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
