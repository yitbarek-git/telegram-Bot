import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from app.config import ADMIN_ID, DEFAULT_COURSE, DEFAULT_LANGUAGE
from app.translations import t
from app.keyboards.inline import main_menu_keyboard, approval_keyboard
from app.database.queries import (
    get_user_by_telegram_id,
    upsert_user,
    get_course,
    create_or_update_payment,
)

logger = logging.getLogger(__name__)

CHOICE, NAME, PAYMENT = range(3)


def get_user_lang(user_id: int) -> str:
    user = get_user_by_telegram_id(user_id)
    if user and user.get("language"):
        return user["language"]
    return DEFAULT_LANGUAGE


def format_course_info(course_id: str, lang: str) -> str:
    course = get_course(course_id)
    if not course:
        return ""
    return t(
        "course_info",
        lang,
        title=course.get("title", ""),
        price=course.get("price", ""),
        telebirr=course.get("telebirr_number", ""),
        cbe=course.get("cbe_number", ""),
        description=course.get("description", ""),
    )


async def menu_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles main menu button clicks during CHOICE state."""
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user
    lang = get_user_lang(user.id)

    if data == "join_freshman":
        await query.edit_message_text(
            t("enter_name", lang),
            parse_mode="Markdown",
        )
        return NAME

    if data == "how_it_works":
        course_str = format_course_info(DEFAULT_COURSE, lang)
        await query.edit_message_text(
            t("how_it_works", lang, course_info=course_str),
            reply_markup=main_menu_keyboard(lang),
            parse_mode="Markdown",
        )
        return CHOICE

    if data == "support":
        await query.edit_message_text(
            t("support", lang),
            reply_markup=main_menu_keyboard(lang),
            parse_mode="Markdown",
        )
        return CHOICE

    if data == "cancel_flow":
        await query.edit_message_text(t("cancel_success", lang), parse_mode="Markdown")
        return ConversationHandler.END

    return CHOICE


async def receive_student_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives student full name and displays payment details."""
    name = update.message.text.strip()
    user = update.effective_user
    lang = get_user_lang(user.id)

    if len(name) < 5:
        await update.message.reply_text(
            t("name_too_short", lang),
            parse_mode="Markdown",
        )
        return NAME

    # Persist updated name in database
    upsert_user(
        telegram_id=user.id,
        full_name=name,
        username=user.username,
        language=lang,
    )

    context.user_data["name"] = name
    context.user_data["course_id"] = DEFAULT_COURSE

    course_str = format_course_info(DEFAULT_COURSE, lang)
    await update.message.reply_text(
        t("payment_instruction", lang, course_info=course_str),
        parse_mode="Markdown",
    )
    return PAYMENT


async def payment_stage_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Routes incoming message in PAYMENT state (photo, document, text, sticker)."""
    message = update.message
    if not message:
        return PAYMENT

    user = update.effective_user
    lang = get_user_lang(user.id)

    if message.photo:
        return await handle_payment_upload(update, context, file_type="photo")

    if message.document:
        mime = (message.document.mime_type or "").lower()
        if not mime.startswith("image/"):
            await message.reply_text(t("not_an_image", lang), parse_mode="Markdown")
            return PAYMENT
        return await handle_payment_upload(update, context, file_type="document")

    if message.sticker:
        await message.reply_text(t("sticker_received", lang), parse_mode="Markdown")
        return PAYMENT

    if message.text:
        text = message.text.strip().lower()
        if text in {"cancel", "/cancel"}:
            context.user_data.clear()
            await message.reply_text(t("cancel_success", lang), parse_mode="Markdown")
            return ConversationHandler.END

        await message.reply_text(t("text_received", lang), parse_mode="Markdown")
        return PAYMENT

    await message.reply_text(t("not_an_image", lang), parse_mode="Markdown")
    return PAYMENT


async def handle_payment_upload(
    update: Update, context: ContextTypes.DEFAULT_TYPE, file_type: str
) -> int:
    """Processes verified screenshot file upload and notifies admin."""
    user = update.effective_user
    message = update.message
    lang = get_user_lang(user.id)

    if file_type == "photo":
        file_id = message.photo[-1].file_id
    else:
        file_id = message.document.file_id

    # Ensure user exists in MySQL
    db_user = upsert_user(
        telegram_id=user.id,
        full_name=context.user_data.get("name", user.full_name),
        username=user.username,
        language=lang,
    )
    user_db_id = db_user["id"]
    student_name = db_user["full_name"]
    username_str = f"@{user.username}" if user.username else "No Username"
    course_id = context.user_data.get("course_id", DEFAULT_COURSE)

    # Insert or update payment record in MySQL
    payment_id, is_update, submission_count = create_or_update_payment(
        user_id=user_db_id,
        course_id=course_id,
        file_type=file_type,
        file_id=file_id,
    )

    course = get_course(course_id)
    course_title = course["title"] if course else course_id

    admin_caption = (
        f"🆕 *New Payment Submission*\n\n"
        f"🧾 *Payment ID:* `#{payment_id}`\n"
        f"👤 *Student Name:* {student_name}\n"
        f"📱 *Username:* {username_str}\n"
        f"🆔 *Telegram ID:* `{user.id}`\n"
        f"📚 *Course:* {course_title}\n"
        f"⏳ *Status:* pending\n"
        f"🔁 *Submission Attempt:* {submission_count}"
    )

    # Send receipt directly to admin with approval keyboard
    if ADMIN_ID:
        try:
            if file_type == "photo":
                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=file_id,
                    caption=admin_caption,
                    reply_markup=approval_keyboard(payment_id),
                    parse_mode="Markdown",
                )
            else:
                await context.bot.send_document(
                    chat_id=ADMIN_ID,
                    document=file_id,
                    caption=admin_caption,
                    reply_markup=approval_keyboard(payment_id),
                    parse_mode="Markdown",
                )
        except Exception as e:
            logger.exception("Failed to send screenshot to admin")
            await message.reply_text(
                "⚠️ Screenshot received, but could not notify admin. Please try again later."
            )
            return ConversationHandler.END

    if is_update:
        await message.reply_text(
            t(
                "received_updated",
                lang,
                payment_id=payment_id,
                submission_count=submission_count,
            ),
            parse_mode="Markdown",
        )
    else:
        await message.reply_text(
            t("received_first", lang, payment_id=payment_id),
            parse_mode="Markdown",
        )

    context.user_data.clear()
    return ConversationHandler.END
