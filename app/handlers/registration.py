import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from app.config import (
    ADMIN_IDS,
    DEFAULT_COURSE,
    DEFAULT_PRICE,
    TELEBIRR_NUMBER,
    TELEBIRR_NAME,
    CBE_ACCOUNT,
    CBE_NAME,
    DEFAULT_LANGUAGE,
)
from app.translations import t
from app.keyboards.inline import (
    main_menu_keyboard,
    payment_methods_keyboard,
    post_instruction_keyboard,
    approval_keyboard,
)
from app.storage import (
    get_user_by_telegram_id,
    upsert_user,
    get_course,
    create_or_update_payment,
)

logger = logging.getLogger(__name__)

WAITING_RECEIPT = 1


def get_user_lang(user_id: int) -> str:
    user = get_user_by_telegram_id(user_id)
    if user and user.get("language"):
        return user["language"]
    return DEFAULT_LANGUAGE


async def menu_callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles interactive navigation across main menu, course info, and payment methods."""
    query = update.callback_query
    if not query:
        return ConversationHandler.END

    await query.answer()
    data = query.data or ""
    user = query.from_user
    lang = get_user_lang(user.id)

    # 1. Main menu
    if data == "main_menu":
        await query.edit_message_text(
            t("welcome", lang),
            reply_markup=main_menu_keyboard(lang),
            parse_mode=None,
        )
        return ConversationHandler.END

    # 2. View Freshman Courses
    if data == "view_courses":
        await query.edit_message_text(
            t("courses_overview", lang),
            reply_markup=payment_methods_keyboard(lang),
            parse_mode=None,
        )
        return ConversationHandler.END

    # 3. Payment options
    if data == "pay_menu":
        await query.edit_message_text(
            t("payment_menu_text", lang),
            reply_markup=payment_methods_keyboard(lang),
            parse_mode=None,
        )
        return ConversationHandler.END

    # 4. Telebirr details
    if data == "pay_method:telebirr":
        context.user_data["selected_method"] = "Telebirr"
        instructions = t(
            "telebirr_instructions",
            lang,
            phone=TELEBIRR_NUMBER,
            name=TELEBIRR_NAME,
        )
        await query.edit_message_text(
            instructions,
            reply_markup=post_instruction_keyboard(lang),
            parse_mode=None,
        )
        return ConversationHandler.END

    # 5. CBE Bank details
    if data == "pay_method:cbe":
        context.user_data["selected_method"] = "CBE Bank Transfer"
        instructions = t(
            "cbe_instructions",
            lang,
            account=CBE_ACCOUNT,
            name=CBE_NAME,
        )
        await query.edit_message_text(
            instructions,
            reply_markup=post_instruction_keyboard(lang),
            parse_mode=None,
        )
        return ConversationHandler.END

    # 6. User clicks 'Submit Payment' / 'Send Receipt'
    if data == "submit_receipt":
        await query.message.reply_text(
            t("ask_receipt", lang),
            parse_mode=None,
        )
        return WAITING_RECEIPT

    # 7. Help menu
    if data == "help_menu":
        await query.edit_message_text(
            t("help_text", lang),
            reply_markup=main_menu_keyboard(lang),
            parse_mode=None,
        )
        return ConversationHandler.END

    return ConversationHandler.END


async def start_receipt_submission_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Triggered by /pay or direct message asking to upload payment receipt."""
    user = update.effective_user
    lang = get_user_lang(user.id)
    await update.message.reply_text(
        t("ask_receipt", lang),
        parse_mode=None,
    )
    return WAITING_RECEIPT


async def receive_payment_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives receipt photo or document image and registers pending payment."""
    message = update.message
    if not message:
        return WAITING_RECEIPT

    user = update.effective_user
    lang = get_user_lang(user.id)

    # Allow cancellation
    if message.text and message.text.strip().lower() in ("/cancel", "cancel"):
        context.user_data.clear()
        await message.reply_text(
            t("cancel_success", lang),
            reply_markup=main_menu_keyboard(lang),
            parse_mode=None,
        )
        return ConversationHandler.END

    # Detect photo
    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
        return await process_and_notify_payment(update, context, file_type, file_id)

    # Detect document image (e.g. uncompressed PNG/JPG)
    if message.document:
        mime = (message.document.mime_type or "").lower()
        if mime.startswith("image/") or (message.document.file_name or "").lower().endswith((".png", ".jpg", ".jpeg")):
            file_id = message.document.file_id
            file_type = "document"
            return await process_and_notify_payment(update, context, file_type, file_id)
        else:
            await message.reply_text(t("not_an_image", lang), parse_mode=None)
            return WAITING_RECEIPT

    # If text is sent during WAITING_RECEIPT, remind them to send an image/photo
    await message.reply_text(t("not_an_image", lang), parse_mode=None)
    return WAITING_RECEIPT


async def direct_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles photo/document sent directly without entering the conversation state first."""
    message = update.message
    if not message:
        return

    # Check photo
    if message.photo:
        file_id = message.photo[-1].file_id
        await process_and_notify_payment(update, context, "photo", file_id)
        return

    # Check document image
    if message.document:
        mime = (message.document.mime_type or "").lower()
        if mime.startswith("image/") or (message.document.file_name or "").lower().endswith((".png", ".jpg", ".jpeg")):
            file_id = message.document.file_id
            await process_and_notify_payment(update, context, "document", file_id)
            return


async def process_and_notify_payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    file_type: str,
    file_id: str,
) -> int:
    """Records payment as pending and sends notification to admins with approval keyboard."""
    user = update.effective_user
    message = update.message
    lang = get_user_lang(user.id)

    # Ensure student profile exists in JSON storage
    db_user = upsert_user(
        telegram_id=user.id,
        full_name=user.full_name or "Student",
        username=user.username,
        language=lang,
    )
    student_name = db_user.get("full_name") or user.full_name or "Student"
    username_str = f"@{user.username}" if user.username else "No Username"
    payment_method = context.user_data.get("selected_method", "Telebirr / CBE")

    # Record payment in JSON storage
    payment_id, is_update, submission_count = create_or_update_payment(
        telegram_id=user.id,
        file_type=file_type,
        file_id=file_id,
        payment_method=payment_method,
        amount=DEFAULT_PRICE,
        course_id=DEFAULT_COURSE,
    )

    admin_caption = (
        "🆕 New Payment Submission\n\n"
        f"Student: {student_name}\n"
        f"Username: {username_str}\n"
        f"Telegram ID: {user.id}\n"
        f"Course: Freshman Package (All Subjects)\n"
        f"Payment Method: {payment_method}\n"
        f"Amount: {DEFAULT_PRICE}\n"
        "Status: Pending\n"
        f"Receipt ID: #{payment_id}\n"
        f"Submission Attempt: {submission_count}"
    )

    # Notify all configured admins with photo and interactive approval buttons
    for admin_id in ADMIN_IDS:
        try:
            if file_type == "photo":
                await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=file_id,
                    caption=admin_caption,
                    reply_markup=approval_keyboard(payment_id),
                    parse_mode=None,
                )
            else:
                await context.bot.send_document(
                    chat_id=admin_id,
                    document=file_id,
                    caption=admin_caption,
                    reply_markup=approval_keyboard(payment_id),
                    parse_mode=None,
                )
        except Exception as e:
            logger.warning("Could not forward receipt to admin %s: %s", admin_id, e)

    # Send confirmation to the student
    if is_update:
        await message.reply_text(
            t("receipt_updated_pending", lang, payment_id=payment_id, submission_count=submission_count),
            reply_markup=main_menu_keyboard(lang),
            parse_mode=None,
        )
    else:
        await message.reply_text(
            t("receipt_received_pending", lang, payment_id=payment_id),
            reply_markup=main_menu_keyboard(lang),
            parse_mode=None,
        )

    context.user_data.clear()
    return ConversationHandler.END


async def fallback_unrelated_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles any random/unrelated user input (text, sticker, voice, video) without crashing.
    Gracefully guides them back to the Ethiopian freshman course menu.
    """
    message = update.message
    if not message:
        return

    user = update.effective_user
    lang = get_user_lang(user.id) if user else DEFAULT_LANGUAGE

    await message.reply_text(
        t("unrelated_message", lang),
        reply_markup=main_menu_keyboard(lang),
        parse_mode=None,
    )
