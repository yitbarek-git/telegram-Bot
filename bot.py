import os
import json
import logging
from datetime import datetime

from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ================= ENV =================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
GROUP_ID = os.getenv("GROUP_ID")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")

try:
    ADMIN_ID = int(ADMIN_ID)
    GROUP_ID = int(GROUP_ID)
except Exception:
    raise ValueError("ADMIN_ID or GROUP_ID must be integers")

TELEBIRR_NUMBER = "0929781996"
COURSE_PRICE = "400 ETB"

# ================= CONFIG =================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

DB_FILE = "users.json"

COURSES = {
    "freshman": {
        "title": "Freshman Courses",
        "price": COURSE_PRICE,
        "number": TELEBIRR_NUMBER,
        "description": "PDFs + Videos + Past Exams",
    }
}

DEFAULT_COURSE = "freshman"

# Conversation states
CHOICE, NAME, PAYMENT = range(3)

# In-memory DB
users_db = {}


# ================= STORAGE HELPERS =================
def load_users():
    global users_db
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            users_db = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users_db = {}
    except Exception as e:
        logger.error(f"Failed to load users: {e}")
        users_db = {}


def save_users():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(users_db, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save users: {e}")


def get_user_record(user_id: int):
    return users_db.get(str(user_id))


def set_user_record(user_id: int, data: dict):
    users_db[str(user_id)] = data
    save_users()


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


# ================= UI HELPERS =================
def main_menu_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎓 Join Freshman Course", callback_data="join_freshman")],
            [InlineKeyboardButton("ℹ️ How it works", callback_data="how_it_works")],
            [InlineKeyboardButton("🆘 Help", callback_data="support")],
            [InlineKeyboardButton("✖ Cancel", callback_data="cancel_flow")],
        ]
    )


def approval_keyboard(user_id: int):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}"),
            ]
        ]
    )


def course_info():
    c = COURSES[DEFAULT_COURSE]
    return (
        f"📚 *Course:* {c['title']}\n"
        f"💰 *Price:* {c['price']}\n"
        f"📞 *Telebirr:* `{c['number']}`\n"
        f"📦 *Includes:* {c['description']}"
    )


# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()

    await update.message.reply_text(
        "👋 Welcome to A+ Academy!\n\nChoose an option:",
        reply_markup=main_menu_keyboard(),
    )
    return CHOICE


async def menu_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "join_freshman":
        await query.edit_message_text(
            "📝 Send your *full name* exactly as you want it recorded.\n"
            "Example: *Amanuel Tadesse*",
            parse_mode="Markdown",
        )
        return NAME

    if query.data == "how_it_works":
        await query.edit_message_text(
            "📖 *How it works*\n\n"
            "1️⃣ Send your full name\n"
            "2️⃣ Pay using Telebirr\n"
            "3️⃣ Send the screenshot\n"
            "4️⃣ Admin checks it\n"
            "5️⃣ You receive the private group link\n\n"
            f"{course_info()}",
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown",
        )
        return CHOICE

    if query.data == "support":
        await query.edit_message_text(
            "🆘 *Support*\n\n"
            "• First send your full name\n"
            "• Pay using the displayed Telebirr number\n"
            "• Send the payment screenshot as a photo or image file\n"
            "• If you send text or a sticker by mistake, just send the screenshot again",
            parse_mode="Markdown",
        )
        return CHOICE

    if query.data == "cancel_flow":
        await query.edit_message_text("❌ Cancelled. Type /start when ready again.")
        return ConversationHandler.END

    return CHOICE


async def payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text.strip()

    if len(name) < 5:
        await update.message.reply_text(
            "❌ Please enter a valid full name.\n"
            "Example: *Amanuel Tadesse*",
            parse_mode="Markdown",
        )
        return NAME

    context.user_data["name"] = name
    context.user_data["course"] = DEFAULT_COURSE

    await update.message.reply_text(
        f"💳 *Payment Instructions*\n\n"
        f"{course_info()}\n\n"
        "➡️ After payment, send the *screenshot* as a photo or image file.\n"
        "📸 Ready? Send your screenshot now.",
        parse_mode="Markdown",
    )
    return PAYMENT


async def payment_stage_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message

    if not message:
        return PAYMENT

    if message.photo:
        return await receive_payment_photo(update, context)

    if message.document:
        return await receive_payment_document(update, context)

    if message.sticker:
        await message.reply_text(
            "😕 I received a sticker.\n\n"
            "Please send the *payment screenshot* as a photo or image file.",
            parse_mode="Markdown",
        )
        return PAYMENT

    if message.text:
        text = message.text.strip().lower()
        if text in {"cancel", "/cancel"}:
            return await cancel(update, context)

        await message.reply_text(
            "📝 I received text, not a screenshot.\n\n"
            "Please send the *payment screenshot* as a photo or image file.",
            parse_mode="Markdown",
        )
        return PAYMENT

    await message.reply_text(
        "⚠️ Unsupported message type.\n\n"
        "Please send the *payment screenshot* as a photo or image file.",
        parse_mode="Markdown",
    )
    return PAYMENT


async def receive_payment_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    message = update.message
    user_id = user.id

    photo_id = message.photo[-1].file_id
    name = context.user_data.get("name", user.full_name)
    username = f"@{user.username}" if user.username else "No Username"
    previous = get_user_record(user_id)

    record = {
        "name": name,
        "username": username,
        "date": now_str(),
        "updated_at": now_str(),
        "status": "pending",
        "course": context.user_data.get("course", DEFAULT_COURSE),
        "file_type": "photo",
        "file_id": photo_id,
        "submission_count": (previous.get("submission_count", 0) + 1) if previous else 1,
    }
    set_user_record(user_id, record)

    admin_caption = (
        f"🆕 *New Enrollment / Renewal*\n\n"
        f"👤 *Name:* {name}\n"
        f"📱 *Username:* {username}\n"
        f"🆔 *Telegram ID:* `{user_id}`\n"
        f"📚 *Course:* {COURSES[record['course']]['title']}\n"
        f"⏳ *Status:* pending\n"
        f"🔁 *Submission:* {record['submission_count']}"
    )

    try:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_id,
            caption=admin_caption,
            reply_markup=approval_keyboard(user_id),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.exception("Failed to send photo to admin")
        await message.reply_text(
            f"⚠️ Screenshot received, but admin notification failed.\n\nError: {e}"
        )
        return ConversationHandler.END

    if previous and previous.get("status") == "pending":
        await message.reply_text(
            "🔄 Updated screenshot received.\n"
            "I sent the latest one to the admin."
        )
    elif previous and previous.get("status") == "approved":
        await message.reply_text(
            "🔄 New payment screenshot received.\n"
            "It has been sent for verification again."
        )
    else:
        await message.reply_text(
            "📸 Screenshot received!\n"
            "The admin will verify it soon.\n\n"
            "Use /status to check your current state."
        )

    return ConversationHandler.END


async def receive_payment_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    document = message.document
    mime = (document.mime_type or "").lower()

    if not mime.startswith("image/"):
        await message.reply_text(
            "❌ That file is not an image screenshot.\n\n"
            "Please send the payment screenshot as a *photo* or an *image file* (PNG, JPG).",
            parse_mode="Markdown",
        )
        return PAYMENT

    user = update.effective_user
    user_id = user.id

    file_id = document.file_id
    name = context.user_data.get("name", user.full_name)
    username = f"@{user.username}" if user.username else "No Username"
    previous = get_user_record(user_id)

    record = {
        "name": name,
        "username": username,
        "date": now_str(),
        "updated_at": now_str(),
        "status": "pending",
        "course": context.user_data.get("course", DEFAULT_COURSE),
        "file_type": "document",
        "file_id": file_id,
        "submission_count": (previous.get("submission_count", 0) + 1) if previous else 1,
    }
    set_user_record(user_id, record)

    admin_caption = (
        f"🆕 *New Enrollment / Renewal*\n\n"
        f"👤 *Name:* {name}\n"
        f"📱 *Username:* {username}\n"
        f"🆔 *Telegram ID:* `{user_id}`\n"
        f"📚 *Course:* {COURSES[record['course']]['title']}\n"
        f"⏳ *Status:* pending\n"
        f"🔁 *Submission:* {record['submission_count']}"
    )

    try:
        await context.bot.send_document(
            chat_id=ADMIN_ID,
            document=file_id,
            caption=admin_caption,
            reply_markup=approval_keyboard(user_id),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.exception("Failed to send document to admin")
        await message.reply_text(
            f"⚠️ Screenshot received, but admin notification failed.\n\nError: {e}"
        )
        return ConversationHandler.END

    if previous and previous.get("status") == "pending":
        await message.reply_text(
            "🔄 Updated image file received.\n"
            "I sent the latest one to the admin."
        )
    elif previous and previous.get("status") == "approved":
        await message.reply_text(
            "🔄 New payment file received.\n"
            "It has been sent for verification again."
        )
    else:
        await message.reply_text(
            "📎 Image file received!\n"
            "The admin will verify it soon.\n\n"
            "Use /status to check your current state."
        )

    return ConversationHandler.END


async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ You are not allowed to do that.", show_alert=True)
        return

    data = query.data
    if "_" not in data:
        return

    action, user_id_str = data.split("_", 1)

    try:
        target_user_id = int(user_id_str)
    except ValueError:
        await query.answer("Invalid user ID.", show_alert=True)
        return

    record = get_user_record(target_user_id)
    if not record:
        await query.edit_message_caption(
            caption=(query.message.caption or "") + "\n\n❌ User record not found.",
            parse_mode="Markdown",
        )
        return

    try:
        if action == "approve":
            if record.get("status") == "approved":
                await query.edit_message_caption(
                    caption=(query.message.caption or "") + "\n\n✅ Already approved.",
                    parse_mode="Markdown",
                )
                return

            invite = await context.bot.create_chat_invite_link(
                chat_id=GROUP_ID,
                member_limit=1,
            )

            await context.bot.send_message(
                chat_id=target_user_id,
                text=(
                    "✅ *Payment verified!*\n\n"
                    "🎉 Welcome to *A+ Academy*.\n\n"
                    f"🔗 Your private group link:\n{invite.invite_link}\n\n"
                    "This link can be used once."
                ),
                parse_mode="Markdown",
            )

            record["status"] = "approved"
            record["approved_at"] = now_str()
            record["updated_at"] = now_str()
            set_user_record(target_user_id, record)

            await query.edit_message_caption(
                caption=(query.message.caption or "") + "\n\n✅ *APPROVED*",
                reply_markup=None,
                parse_mode="Markdown",
            )

        elif action == "reject":
            if record.get("status") == "rejected":
                await query.edit_message_caption(
                    caption=(query.message.caption or "") + "\n\n❌ Already rejected.",
                    parse_mode="Markdown",
                )
                return

            await context.bot.send_message(
                chat_id=target_user_id,
                text=(
                    "❌ *Payment not approved*\n\n"
                    "Your screenshot could not be verified.\n"
                    "Please try again with /start."
                ),
                parse_mode="Markdown",
            )

            record["status"] = "rejected"
            record["rejected_at"] = now_str()
            record["updated_at"] = now_str()
            set_user_record(target_user_id, record)

            await query.edit_message_caption(
                caption=(query.message.caption or "") + "\n\n❌ *REJECTED*",
                reply_markup=None,
                parse_mode="Markdown",
            )

    except Exception as e:
        logger.exception("Admin decision failed")
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"⚠️ Error while processing {action} for user {target_user_id}:\n{e}",
        )
        await query.answer("Error occurred. Check logs.", show_alert=True)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    record = get_user_record(user.id)

    if not record:
        await update.message.reply_text("📭 No record found yet.\nUse /start to begin.")
        return

    await update.message.reply_text(
        f"📊 *Your status*\n\n"
        f"👤 *Name:* {record.get('name', 'Unknown')}\n"
        f"📚 *Course:* {COURSES[record.get('course', DEFAULT_COURSE)]['title']}\n"
        f"🔖 *Status:* {record.get('status', 'unknown').upper()}\n"
        f"🕒 *Last update:* {record.get('updated_at', record.get('date', 'N/A'))}",
        parse_mode="Markdown",
    )


async def myinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    record = get_user_record(user.id)

    if not record:
        await update.message.reply_text("No information found. Send /start to begin.")
        return

    await update.message.reply_text(
        f"📋 *Your submission details*\n\n"
        f"📝 *Name:* {record.get('name')}\n"
        f"🆔 *Telegram ID:* `{user.id}`\n"
        f"📚 *Course:* {COURSES[record.get('course', DEFAULT_COURSE)]['title']}\n"
        f"🔖 *Status:* {record.get('status', 'unknown')}\n"
        f"📅 *Submitted on:* {record.get('date')}\n"
        f"🔄 *Submission #:* {record.get('submission_count', 1)}\n"
        f"🕒 *Last update:* {record.get('updated_at', 'N/A')}",
        parse_mode="Markdown",
    )


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    total = len(users_db)
    approved = sum(1 for v in users_db.values() if v.get("status") == "approved")
    pending = sum(1 for v in users_db.values() if v.get("status") == "pending")
    rejected = sum(1 for v in users_db.values() if v.get("status") == "rejected")

    pending_list = []
    for uid, data in users_db.items():
        if data.get("status") == "pending":
            pending_list.append(f"• {data.get('name')} (ID: `{uid}`)")

    pending_text = "\n".join(pending_list) if pending_list else "None"

    await update.message.reply_text(
        f"📊 *Bot Statistics*\n\n"
        f"👥 Total users: {total}\n"
        f"✅ Approved: {approved}\n"
        f"⏳ Pending: {pending}\n"
        f"❌ Rejected: {rejected}\n\n"
        f"*Pending users:*\n{pending_text}",
        parse_mode="Markdown",
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Cancelled.\nType /start to begin again.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 *Help*\n\n"
        "1️⃣ Type /start\n"
        "2️⃣ Send your full name\n"
        "3️⃣ Pay the displayed amount via Telebirr\n"
        "4️⃣ Send the screenshot (photo or image file)\n\n"
        "• Use /status to check your approval status\n"
        "• Use /myinfo to see your submitted details\n"
        "• Use /cancel to stop any process",
        parse_mode="Markdown",
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Unhandled error: %s", context.error)
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"⚠️ Bot error:\n{context.error}",
        )
    except Exception:
        pass


# ================= MAIN =================
def main():
    load_users()

    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOICE: [
                CallbackQueryHandler(
                    menu_action,
                    pattern="^(join_freshman|how_it_works|support|cancel_flow)$",
                )
            ],
            NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, payment_info),
                CommandHandler("cancel", cancel),
            ],
            PAYMENT: [
                MessageHandler(filters.ALL, payment_stage_router),
                CommandHandler("cancel", cancel),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("help", help_command),
            CommandHandler("start", start),
        ],
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("myinfo", myinfo))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CallbackQueryHandler(admin_decision, pattern="^(approve_|reject_)"))
    app.add_error_handler(error_handler)

    print("🚀 Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
