import os
import re
import time
import logging
from dataclasses import dataclass
from html import escape

from dotenv import load_dotenv
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler, CallbackQueryHandler,
)
from telegram.request import HTTPXRequest

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0") or 0)
GROUP_ID = int(os.getenv("GROUP_ID", "0") or 0)

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing in environment.")

if ADMIN_ID <= 0:
    raise RuntimeError(
        f"ADMIN_ID must be a positive integer (your personal Telegram id). Got: {ADMIN_ID}"
    )

# GROUP_ID is a chat id for a group/supergroup → always NEGATIVE.
#   supergroup: -1001234567890
#   legacy group: -123456789
if GROUP_ID >= 0:
    raise RuntimeError(
        f"GROUP_ID must be a negative integer (supergroup id looks like -1001234567890).\n"
        f"Got: {GROUP_ID}\n"
        f"Tip: send any message in the group, then open "
        f"https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates and look for "
        f"\"chat\": {{\"id\": -100..., \"type\": \"supergroup\"}}."
    )

COURSE_NAME = "All Freshman Courses"
COURSE_NAME_AM = "የመጀመሪያ ዓመት ትምህርቶች ሁሉም"
COURSE_PRICE = "300 ETB"

TELEBIRR_NUMBER = "0929781996"
CBE_ACCOUNT_NAME = "Yitbarek Yohans"
CBE_ACCOUNT_NUMBER = "1000316427735"
CBE_BANK_NAME = "CBE · ንግድ ባንክ"

# Defensive limits
MAX_CAPTION_LEN = 1024
MIN_NAME_LEN = 2
MAX_NAME_LEN = 100
MIN_PHOTO_BYTES = 8 * 1024
SUBMIT_COOLDOWN_SEC = 15
START_COOLDOWN_SEC = 3

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("academy-bot")

NAME, PAYMENT = range(2)


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------
@dataclass
class Enrollment:
    user_id: int
    name: str
    username: str | None
    course: str = COURSE_NAME
    status: str = "pending"                # pending | approved | rejected
    admin_message_id: int | None = None
    invite_link: str | None = None
    submitted_at: float = 0.0

users_db: dict[int, Enrollment] = {}
approved_users: set[int] = set()
_last_action: dict[int, float] = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def h(text) -> str:
    return escape(str(text)) if text is not None else ""


def clean_name(raw: str) -> str:
    if not raw:
        return ""
    cleaned = re.sub(r"[\x00-\x1f\x7f]", "", raw)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def cooldown_ok(user_id: int, key_sec: float) -> bool:
    now = time.monotonic()
    last = _last_action.get(user_id, 0.0)
    if now - last < key_sec:
        return False
    _last_action[user_id] = now
    return True


def safe_caption(prefix: str, suffix: str = "") -> str:
    combined = prefix + suffix
    if len(combined) <= MAX_CAPTION_LEN:
        return combined
    room = MAX_CAPTION_LEN - len(suffix) - 20
    trimmed = combined[:max(room, 0)].rstrip()
    return trimmed + " …" + suffix


async def _reply(update: Update, text: str, **kwargs) -> None:
    try:
        await update.effective_message.reply_text(text, **kwargs)
    except Exception:
        uid = getattr(update.effective_user, "id", "?")
        logger.exception("Failed to reply to user %s", uid)


def payment_instructions_html() -> str:
    return (
        f"💵 <b>Price:</b> {h(COURSE_PRICE)} — one payment, all courses.\n"
        f"💵 <b>ዋጋ፦</b> {h(COURSE_PRICE)} — አንድ ክፍያ ለሁሉም ትምህርቶች።\n\n"

        f"💳 <b>Pay via Telebirr</b>\n"
        f"💳 <b>በቴሌብር ይክፈሉ</b>\n"
        f"• Number / ቁጥር: <code>{h(TELEBIRR_NUMBER)}</code>\n\n"

        f"🏦 <b>Or via CBE · ንግድ ባንክ</b>\n"
        f"🏦 <b>ወይም በንግድ ባንክ (CBE)</b>\n"
        f"• Account Name / የሂሳብ ስም: <code>{h(CBE_ACCOUNT_NAME)}</code>\n"
        f"• Account Number / የሂሳብ ቁጥር: <code>{h(CBE_ACCOUNT_NUMBER)}</code>\n\n"

        f"📸 After paying, take a screenshot of the receipt and send it here.\n"
        f"📸 ከከፈሉ በኋላ የደረሰኙን ስክሪንሾት አንስተው እዚህ ይላኩ።"
    )


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user

    if not cooldown_ok(user.id, START_COOLDOWN_SEC):
        return ConversationHandler.END

    context.user_data.clear()

    if user.id == ADMIN_ID:
        await update.message.reply_text(
            "⚠️ You are the admin. Use /status to inspect students.\n"
            "⚠️ እርስዎ አስተዳዳሪ ነዎት። ተማሪዎችን ለማየት /status ይጠቀሙ።",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    if user.id in approved_users:
        await update.message.reply_text(
            "✅ You are already enrolled. Type /help for assistance.\n"
            "✅ አስቀድመው ተመዝግበዋል። እርዳታ ከፈለጉ /help ይጻፉ።",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "👋 <b>Welcome to A+ Academy!</b>\n"
        "👋 <b>ወደ A+ አካዳሚ እንኳን በደህና መጡ!</b>\n\n"
        f"📚 Enroll in <b>{h(COURSE_NAME)}</b> with one payment.\n"
        f"📚 በአንድ ክፍያ <b>{h(COURSE_NAME_AM)}</b> ይመዝገቡ።\n\n"
        "✍️ Type your <b>full name</b>:\n"
        "✍️ <b>ሙሉ ስምዎን</b> ይጻፉ፦",
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove(),
    )
    return NAME


async def payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = clean_name(update.message.text or "")

    if len(name) < MIN_NAME_LEN:
        await _reply(
            update,
            "⚠️ Please send your real name (at least 2 characters).\n"
            "⚠️ እባክዎ እውነተኛ ስምዎን ይጻፉ (ቢያንስ 2 ፊደል)።",
        )
        return NAME
    if len(name) > MAX_NAME_LEN:
        await _reply(
            update,
            "⚠️ Name is too long. Please use 100 characters or fewer.\n"
            "⚠️ ስሙ በጣም ረጅም ነው። ከ100 ፊደል በታች ይጠቀሙ።",
        )
        return NAME

    context.user_data["name"] = name

    await update.message.reply_text(
        payment_instructions_html()
        + "\n\n📸 <b>Send the screenshot now.</b>\n"
          "📸 <b>አሁን ስክሪንሾቱን ይላኩ።</b>",
        parse_mode=ParseMode.HTML,
    )
    return PAYMENT


async def receive_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user

    if user.id == ADMIN_ID:
        await _reply(update, "⚠️ Admin cannot enroll. Use /status to review students.")
        return ConversationHandler.END

    if not update.message.photo:
        await _reply(
            update,
            "⚠️ Please send a <b>screenshot image</b> (not text, not a file).\n"
            "⚠️ እባክዎ <b>የስክሪንሾት ምስል</b> ይላኩ (ጽሑፍ ወይም ፋይል አይደለም)።",
            parse_mode=ParseMode.HTML,
        )
        return PAYMENT

    if user.id in approved_users:
        await _reply(
            update,
            "✅ You're already enrolled — no need to send again.\n"
            "✅ አስቀድመው ተመዝግበዋል — እንደገና መላክ አያስፈልግም።",
        )
        return ConversationHandler.END

    if not cooldown_ok(user.id, SUBMIT_COOLDOWN_SEC):
        await _reply(
            update,
            "⏳ Please wait a few seconds before sending again.\n"
            "⏳ እባክዎ ለጥቂት ሰከንዶች ቆይተው እንደገና ይላኩ።",
        )
        return PAYMENT

    best = update.message.photo[-1]
    if best.file_size and best.file_size < MIN_PHOTO_BYTES:
        await _reply(
            update,
            "⚠️ The image is too small to read. Please send a full screenshot.\n"
            "⚠️ ምስሉ በጣም ትንሽ ነው። ሙሉ ስክሪንሾት ይላኩ።",
        )
        return PAYMENT

    previous = users_db.get(user.id)
    if previous and previous.status == "pending":
        previous.status = "rejected"
        previous.invite_link = None
        logger.info("User %s resubmitted; previous pending marked rejected", user.id)

    photo_file = best.file_id
    name = context.user_data.get("name", "Unknown")
    if not name or name == "Unknown":
        name = clean_name(user.full_name or "") or "Unknown"

    enrollment = Enrollment(
        user_id=user.id,
        name=name,
        username=user.username,
        submitted_at=time.time(),
    )
    users_db[user.id] = enrollment

    keyboard = [[
        InlineKeyboardButton("✅ Approve", callback_data=f"approve:{user.id}"),
        InlineKeyboardButton("❌ Reject",  callback_data=f"reject:{user.id}"),
    ]]

    username_display = f"@{h(user.username)}" if user.username else "<i>No username</i>"
    caption_body = (
        f"🚨 <b>New Enrollment Request</b>\n\n"
        f"👤 Name: {h(name)}\n"
        f"📚 Course: {h(COURSE_NAME)}\n"
        f"🔗 Username: {username_display}\n"
        f"🆔 ID: <code>{user.id}</code>"
    )
    caption = safe_caption(caption_body, "")

    try:
        sent = await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_file,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        enrollment.admin_message_id = sent.message_id
    except Exception:
        logger.exception("Failed to forward payment to admin for user %s", user.id)
        await _reply(
            update,
            "⚠️ We couldn't reach the admin right now. Please try again later.\n"
            "⚠️ ለአስተዳዳሪው መልእክት መላክ አልተቻለም። እባክዎ ቆይተው ይሞክሩ።",
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "✅ <b>Receipt received.</b>\n"
        "✅ <b>ደረሰኙ ደርሷል።</b>\n\n"
        "⏳ An admin will verify your payment shortly.\n"
        "⏳ You'll get your private group link once approved.\n"
        "⏳ አስተዳዳሪው ክፍያዎን በቅርቡ ያረጋግጣል።\n"
        "⏳ ሲፈቀድ የግል ቡድንዎ ሊንክ ይደርስዎታል።",
        parse_mode=ParseMode.HTML,
    )
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "Enrollment cancelled. Type /start to try again.\n"
        "ምዝገባው ተሰርዟል። እንደገና ለመጀመር /start ይጻፉ።",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "ℹ️ <b>Commands</b>\n"
        "/start  – Begin enrollment · ምዝገባ ለመጀመር\n"
        "/cancel – Cancel enrollment · ምዝገባን ለመሰረዝ\n"
        "/help   – Show this message · ይህን መልእክት ለማየት",
        parse_mode=ParseMode.HTML,
    )


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin-only: /status <user_id>"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Not authorized.")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: <code>/status &lt;user_id&gt;</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid user id.")
        return

    e = users_db.get(uid)
    if not e:
        await update.message.reply_text(
            f"No record for <code>{uid}</code>.", parse_mode=ParseMode.HTML
        )
        return

    await update.message.reply_text(
        f"👤 <b>{h(e.name)}</b>\n"
        f"🆔 <code>{e.user_id}</code>\n"
        f"🔗 @{h(e.username) if e.username else '—'}\n"
        f"📚 {h(e.course)}\n"
        f"📌 Status: <b>{h(e.status)}</b>\n"
        f"🔑 Invite: {'<i>issued</i>' if e.invite_link else '<i>—</i>'}",
        parse_mode=ParseMode.HTML,
    )


# ---------------------------------------------------------------------------
# Admin decision
# ---------------------------------------------------------------------------
async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer("Not authorized.", show_alert=True)
        return

    await query.answer()

    try:
        action, user_id_str = query.data.split(":", 1)
        student_id = int(user_id_str)
    except (ValueError, AttributeError):
        logger.warning("Malformed callback data: %s", getattr(query, "data", "?"))
        return

    enrollment = users_db.get(student_id)
    if not enrollment:
        try:
            await query.edit_message_caption(
                caption=safe_caption(
                    query.message.caption_html or "",
                    "\n\n⚠️ <b>STATUS: UNKNOWN USER</b>",
                ),
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            await context.bot.send_message(
                ADMIN_ID,
                f"Unknown user <code>{student_id}</code>.",
                parse_mode=ParseMode.HTML,
            )
        return

    if enrollment.status != "pending":
        await query.answer(f"Already {enrollment.status}.", show_alert=True)
        return

    if action == "approve":
        try:
            if not enrollment.invite_link:
                link = await context.bot.create_chat_invite_link(
                    chat_id=GROUP_ID,
                    member_limit=1,
                    name=f"student_{student_id}",
                )
                enrollment.invite_link = link.invite_link

            await context.bot.send_message(
                chat_id=student_id,
                text=(
                    "🎉 <b>Payment verified — welcome to A+ Academy!</b>\n"
                    "🎉 <b>ክፍያዎ ተረጋግጧል — ወደ A+ አካዳሚ እንኳን በደህና መጡ!</b>\n\n"
                    "👉 Tap the link below to join your private class group:\n"
                    "👉 የግል ትምህርት ቡድንዎን ለመቀላቀል ከታች ያለውን ሊንክ ይጫኑ፦\n"
                    f"{h(enrollment.invite_link)}\n\n"
                    "🔒 This link works once — please do not share it.\n"
                    "🔒 ሊንኩ አንድ ጊዜ ብቻ ይሰራል — እባክዎ አያጋሩት።"
                ),
                parse_mode=ParseMode.HTML,
            )
            enrollment.status = "approved"
            approved_users.add(student_id)

            new_caption = safe_caption(
                query.message.caption_html or "",
                "\n\n✅ <b>STATUS: APPROVED</b>",
            )
            try:
                await query.edit_message_caption(caption=new_caption, parse_mode=ParseMode.HTML)
            except Exception:
                await context.bot.send_message(
                    ADMIN_ID,
                    f"✅ Approved user <code>{student_id}</code>.",
                    parse_mode=ParseMode.HTML,
                )

        except Exception as e:
            logger.exception("Error approving user %s", student_id)
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    f"❌ Could not approve <code>{student_id}</code>: {h(e)}\n"
                    f"Check: bot is an admin in the group with <i>invite users</i> rights."
                ),
                parse_mode=ParseMode.HTML,
            )

    elif action == "reject":
        try:
            await context.bot.send_message(
                chat_id=student_id,
                text=(
                    "❌ <b>Payment verification failed.</b>\n"
                    "❌ <b>የክፍያ ማረጋገጫው አልተሳካም።</b>\n\n"
                    "The receipt could not be verified. Please contact support, or type /start to try again with a clearer screenshot.\n"
                    "ደረሰኙን ማረጋገጥ አልቻልንም። እባክዎ ድጋፍ ያግኙ፣ ወይም በ /start በመጻፍ ግልጽ ስክሪንሾት እንደገና ይላኩ።"
                ),
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            logger.exception("Failed to notify rejected user %s", student_id)

        enrollment.status = "rejected"
        new_caption = safe_caption(
            query.message.caption_html or "",
            "\n\n❌ <b>STATUS: REJECTED</b>",
        )
        try:
            await query.edit_message_caption(caption=new_caption, parse_mode=ParseMode.HTML)
        except Exception:
            await context.bot.send_message(
                ADMIN_ID,
                f"❌ Rejected user <code>{student_id}</code>.",
                parse_mode=ParseMode.HTML,
            )


# ---------------------------------------------------------------------------
# Error handler
# ---------------------------------------------------------------------------
async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled exception", exc_info=context.error)
    if isinstance(update, Update) and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    "⚠️ Something went wrong. Please try again with /start.\n"
                    "⚠️ የተሳሳተ ነገር ተፈጥሯል። እባክዎ በ /start እንደገና ይሞክሩ።"
                ),
            )
        except Exception:
            pass


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
def build_app() -> Application:
    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=10,
        read_timeout=30,
    )
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .request(request)
        .concurrent_updates(True)
        .build()
    )

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, payment_info)],
            PAYMENT: [MessageHandler(filters.PHOTO, receive_payment)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("start", start),
        ],
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(
        CallbackQueryHandler(admin_decision, pattern=r"^(approve|reject):\d+$")
    )
    app.add_error_handler(on_error)
    return app


def main() -> None:
    app = build_app()
    logger.info("🤖 Bot is running...")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()