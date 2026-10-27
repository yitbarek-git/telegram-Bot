import os
import re
import time
import logging
import threading
from dataclasses import dataclass
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer

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

MAX_CAPTION_LEN = 1024
MIN_NAME_LEN = 3
MAX_NAME_LEN = 100
SUBMIT_COOLDOWN_SEC = 3
START_COOLDOWN_SEC = 2

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("academy-bot")

NAME, PAYMENT = range(2)


class _Health(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass


def _start_health_server():
    port = int(os.environ.get("PORT", 3000))
    server = HTTPServer(("0.0.0.0", port), _Health)
    logger.info("Health server listening on 0.0.0.0:%d", port)
    server.serve_forever()


@dataclass
class Enrollment:
    user_id: int
    name: str
    username: str | None
    course: str = COURSE_NAME
    status: str = "pending"
    admin_message_id: int | None = None
    invite_link: str | None = None
    submitted_at: float = 0.0

users_db: dict[int, Enrollment] = {}
approved_users: set[int] = set()
_last_action: dict[int, float] = {}


def h(text) -> str:
    return escape(str(text)) if text is not None else ""


def clean_name(raw: str) -> str:
    if not raw:
        return ""
    cleaned = re.sub(r"[\x00-\x1f\x7f<>]", "", raw)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if cleaned.isdigit():
        return ""
    if not any(ch.isalpha() for ch in cleaned):
        return ""
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


def _progress_hint(step: int) -> str:
    if step == 1:
        return "\n\n<i>Step 1 of 2 · ደረጃ 1 ከ 2</i>"
    return "\n\n<i>Step 2 of 2 · ደረጃ 2 ከ 2</i>"


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

        f"📸 After paying, send a screenshot of the receipt here.\n"
        f"📸 ከከፈሉ በኋላ የደረሰኙን ስክሪንሾት እዚህ ይላኩ።\n\n"
        f"✅ You can send it as a <b>photo</b> or as an <b>image file</b> — both work.\n"
        f"✅ በ<b>ፎቶ</b> ወይም በ<b>ምስል ፋይል</b> መላክ ይችላሉ — ሁለቱም ይሰራሉ።"
    )


def is_image_document(message) -> bool:
    doc = getattr(message, "document", None)
    if not doc:
        return False
    mime = (doc.mime_type or "").lower()
    if mime.startswith("image/"):
        return True
    fname = (doc.file_name or "").lower()
    return fname.endswith((".png", ".jpg", ".jpeg", ".webp", ".heic", ".heif", ".gif", ".bmp"))


def extract_image_id(message) -> tuple[str | None, str]:
    if getattr(message, "photo", None):
        return message.photo[-1].file_id, "photo"
    if is_image_document(message):
        return message.document.file_id, "document"
    return None, "none"


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

    await update.message.reply_text(
        "👋 <b>Welcome to A+ Academy!</b>\n"
        "👋 <b>ወደ A+ አካዳሚ እንኳን በደህና መጡ!</b>\n\n"
        f"📚 Enroll in <b>{h(COURSE_NAME)}</b> with one payment.\n"
        f"📚 በአንድ ክፍያ <b>{h(COURSE_NAME_AM)}</b> ይመዝገቡ።\n\n"
        "✍️ Type your <b>full name</b>:\n"
        "✍️ <b>ሙሉ ስምዎን</b> ይጻፉ፦"
        + _progress_hint(1),
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove(),
    )
    return NAME


async def payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    file_id, kind = extract_image_id(update.message)
    if file_id:
        await _reply(
            update,
            "📸 Got the image — but first I need your <b>name</b>.\n"
            "📸 ምስሉ ደርሷል — ግን መጀመሪያ <b>ስምዎን</b> እፈልጋለሁ።\n\n"
            "✍️ Type your full name:\n"
            "✍️ ሙሉ ስምዎን ይጻፉ፦",
            parse_mode=ParseMode.HTML,
        )
        return NAME

    if not update.message.text:
        await _reply(
            update,
            "✍️ Please type your <b>full name</b> as text:\n"
            "✍️ እባክዎ <b>ሙሉ ስምዎን</b> በጽሑፍ ይጻፉ፦",
            parse_mode=ParseMode.HTML,
        )
        return NAME

    name = clean_name(update.message.text)

    if not name or len(name) < MIN_NAME_LEN:
        await _reply(
            update,
            "⚠️ Please type your <b>real name using letters</b> (at least 2 characters).\n"
            "⚠️ እባክዎ <b>በፊደል</b> እውነተኛ ስምዎን ይጻፉ (ቢያንስ 2 ፊደል)።\n\n"
            "✍️ Type your full name:\n"
            "✍️ ሙሉ ስምዎን ይጻፉ፦",
            parse_mode=ParseMode.HTML,
        )
        return NAME
    if len(name) > MAX_NAME_LEN:
        await _reply(
            update,
            "⚠️ Name is too long — please use 100 characters or fewer.\n"
            "⚠️ ስሙ በጣም ረጅም ነው — ከ100 ፊደል በታች ይጠቀሙ።\n\n"
            "✍️ Type your full name:\n"
            "✍️ ሙሉ ስምዎን ይጻፉ፦",
            parse_mode=ParseMode.HTML,
        )
        return NAME

    context.user_data["name"] = name

    await update.message.reply_text(
        payment_instructions_html()
        + "\n\n📸 <b>Send the screenshot now.</b>\n"
          "📸 <b>አሁን ስክሪንሾቱን ይላኩ።</b>"
        + _progress_hint(2),
        parse_mode=ParseMode.HTML,
    )
    return PAYMENT


async def receive_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user

    if user.id == ADMIN_ID:
        await _reply(update, "⚠️ Admin cannot enroll. Use /status to review students.")
        return ConversationHandler.END

    file_id, kind = extract_image_id(update.message)

    if not file_id:
        await _reply(
            update,
            "⚠️ Please send the <b>screenshot as an image</b> — photo or image file.\n"
            "⚠️ እባክዎ <b>ስክሪንሾቱን እንደ ምስል</b> ይላኩ — ፎቶ ወይም ምስል ፋይል።\n\n"
            "📸 <b>Two easy ways · ሁለት ቀላል መንገዶች:</b>\n"
            "1️⃣ Open your payment app → take a screenshot → in this chat, tap 📎 → <b>Gallery</b> → send\n"
            "2️⃣ Or: tap 📎 → <b>File</b> → pick the image file → send\n\n"
            "1️⃣ የክፍያ መተግበሪያውን ከፍተው ስክሪንሾት ያንሱ → 📎 → <b>ጋለሪ</b> → ይላኩ\n"
            "2️⃣ ወይም 📎 → <b>ፋይል</b> → ምስሉን ይምረጡ → ይላኩ",
            parse_mode=ParseMode.HTML,
        )
        return PAYMENT

    if not cooldown_ok(user.id, SUBMIT_COOLDOWN_SEC):
        await _reply(
            update,
            "⏳ Please wait a moment before sending again.\n"
            "⏳ እባክዎ ለአፍታ ቆይተው እንደገና ይላኩ።",
        )
        return PAYMENT

    previous = users_db.get(user.id)
    if previous and previous.status == "pending":
        previous.status = "rejected"
        previous.invite_link = None
        logger.info("User %s resubmitted; previous pending marked rejected", user.id)

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
    kind_label = "photo" if kind == "photo" else "image file"
    caption_body = (
        f"🚨 <b>New Enrollment Request</b>\n\n"
        f"👤 Name: {h(name)}\n"
        f"📚 Course: {h(COURSE_NAME)}\n"
        f"🔗 Username: {username_display}\n"
        f"🖼 Receipt: <i>{h(kind_label)}</i>\n"
        f"🆔 ID: <code>{user.id}</code>"
    )
    caption = safe_caption(caption_body, "")

    try:
        if kind == "photo":
            sent = await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=file_id,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            sent = await context.bot.send_document(
                chat_id=ADMIN_ID,
                document=file_id,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        enrollment.admin_message_id = sent.message_id
    except Exception:
        logger.exception("Failed to forward payment to admin for user %s", user.id)
        await _reply(
            update,
            "⚠️ We couldn't reach the admin right now. Please try again in a minute.\n"
            "⚠️ ለአስተዳዳሪው መልእክት መላክ አልተቻለም። እባክዎ ከአንድ ደቂቃ በኋላ ይሞክሩ።",
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "✅ <b>Receipt received.</b>\n"
        "✅ <b>ደረሰኙ ደርሷል።</b>\n\n"
        "⏳ An admin will verify your payment shortly.\n"
        "⏳ You'll get your private group link once approved.\n"
        "⏳ አስተዳዳሪው ክፍያዎን በቅርቡ ያረጋግጣል።\n"
        "⏳ ሲፈቀድ የግል ቡድንዎ ሊንክ ይደርስዎታል።\n\n"
        "🔕 You don't need to send anything else.\n"
        "🔕 ተጨማሪ ነገር መላክ አያስፈልግም።",
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
        "ℹ️ <b>How to register · እንዴት እንደሚመዘገቡ</b>\n\n"
        "1️⃣ Type /start to begin.\n"
        "1️⃣ ለመጀመር /start ይጻፉ።\n\n"
        "2️⃣ Send your <b>full name</b> as text.\n"
        "2️⃣ <b>ሙሉ ስምዎን</b> በጽሑፍ ይላኩ።\n\n"
        f"3️⃣ Pay {h(COURSE_PRICE)} via Telebirr or CBE.\n"
        f"3️⃣ {h(COURSE_PRICE)} በቴሌብር ወይም በንግድ ባንክ ይክፈሉ።\n\n"
        "4️⃣ Send the <b>screenshot</b> — photo or image file.\n"
        "4️⃣ <b>ስክሪንሾቱን</b> ይላኩ — ፎቶ ወይም ምስል ፋይል።\n\n"
        "5️⃣ Wait for approval — you'll receive a private group link.\n"
        "5️⃣ ማረጋገጫ ይጠብቁ — የግል ቡድን ሊንክ ይደርስዎታል።\n\n"
        "───────────\n"
        "<b>Commands · ትዕዛዞች</b>\n"
        "/start  · መጀመር · Begin\n"
        "/cancel · መሰረዝ · Cancel\n"
        "/help   · ይህ መልእክት · This help",
        parse_mode=ParseMode.HTML,
    )


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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


async def fallback_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip().lower() if update.message.text else ""

    greetings = {
        "hi", "hello", "hey", "salam", "selam", "ሰላም", "ሰላምታ",
        "good morning", "good afternoon", "good evening",
    }
    if text in greetings:
        await _reply(
            update,
            "👋 Hello! · ሰላም!\n\n"
            "To start enrollment, type /start or send your <b>full name</b>.\n"
            "ለመመዝገብ /start ይጻፉ ወይም <b>ሙሉ ስምዎን</b> ይላኩ።",
            parse_mode=ParseMode.HTML,
        )
    elif context.user_data.get("name"):
        await _reply(
            update,
            "📸 I'm waiting for your <b>screenshot</b>.\n"
            "📸 <b>ስክሪንሾትዎን</b> እየጠበቅኩ ነው።\n\n"
            "Send the receipt as a <b>photo</b> or <b>image file</b>.\n"
            "ደረሰኙን በ<b>ፎቶ</b> ወይም በ<b>ምስል ፋይል</b> ይላኩ።",
            parse_mode=ParseMode.HTML,
        )
    else:
        await _reply(
            update,
            "🤔 I didn't catch that.\n"
            "🤔 ያንን አልገባኝም።\n\n"
            "Type your <b>full name</b> to continue, or /start to restart.\n"
            "<b>ሙሉ ስምዎን</b> ይጻፉ፣ ወይም ለመጀመር /start ይጻፉ።",
            parse_mode=ParseMode.HTML,
        )

    if context.user_data.get("name"):
        return PAYMENT
    return NAME


async def fallback_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    file_id, _ = extract_image_id(update.message)

    if context.user_data.get("name") and file_id:
        return await receive_payment(update, context)

    if context.user_data.get("name"):
        await _reply(
            update,
            "📸 Please send the screenshot as a <b>photo</b> or <b>image file</b>.\n"
            "📸 እባክዎ ስክሪንሾቱን በ<b>ፎቶ</b> ወይም በ<b>ምስል ፋይል</b> ይላኩ።",
            parse_mode=ParseMode.HTML,
        )
        return PAYMENT

    await _reply(
        update,
        "📸 Nice image — but I need your <b>name</b> first.\n"
        "📸 ጥሩ ምስል ነው — ግን መጀመሪያ <b>ስምዎን</b> እፈልጋለሁ።\n\n"
        "✍️ Type your full name:\n"
        "✍️ ሙሉ ስምዎን ይጻፉ፦",
        parse_mode=ParseMode.HTML,
    )
    return NAME


async def catchall_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat = update.effective_chat

    if chat and chat.type in ("group", "supergroup"):
        return

    if user and user.id == ADMIN_ID:
        await _reply(update, "ℹ️ Admin — use /status or /help.")
        return

    file_id, _ = extract_image_id(update.message)
    if file_id:
        await _reply(
            update,
            "📸 Got your image — to enroll, tap /start.\n"
            "📸 ምስሉ ደርሷል — ለመመዝገብ /start ን ይጫኑ።",
            parse_mode=ParseMode.HTML,
        )
        return

    if update.message and update.message.text:
        text = update.message.text.strip().lower()
        greetings = {
            "hi", "hello", "hey", "salam", "selam", "ሰላም", "ሰላምታ",
            "good morning", "good afternoon", "good evening",
            "help", "start", "register", "enroll", "join",
        }
        if text in greetings:
            await _reply(
                update,
                "👋 Hello and welcome!\n"
                "👋 ሰላም፣ እንኳን በደህና መጡ!\n\n"
                "Tap /start to enroll, or /help for the steps.\n"
                "ለመመዝገብ /start ይጫኑ፣ ወይም ደረጃዎቹን ለማየት /help ይጫኑ።",
                parse_mode=ParseMode.HTML,
            )
            return

    await _reply(
        update,
        "👋 Welcome to A+ Academy!\n"
        "👋 ወደ A+ አካዳሚ እንኳን በደህና መጡ!\n\n"
        "To begin enrollment, send /start.\n"
        "ምዝገባን ለመጀመር /start ይላኩ።\n"
        "For help, send /help.\n"
        "ለእርዳታ /help ይላኩ።",
        parse_mode=ParseMode.HTML,
    )


async def catchall_non_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat and chat.type in ("group", "supergroup"):
        return

    msg = update.message
    file_id, _ = extract_image_id(msg) if msg else (None, "none")
    if file_id:
        await _reply(
            update,
            "📸 Got your image — to enroll, tap /start.\n"
            "📸 ምስሉ ደርሷል — ለመመዝገብ /start ን ይጫኑ።",
            parse_mode=ParseMode.HTML,
        )
        return

    await _reply(
        update,
        "🤖 I can work with <b>text</b> and <b>screenshots</b>.\n"
        "🤖 በ<b>ጽሑፍ</b> እና በ<b>ስክሪንሾት</b> ነው የምሰራው።\n\n"
        "Tap /start to enroll.\n"
        "ለመመዝገብ /start ይጫኑ።",
        parse_mode=ParseMode.HTML,
    )


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

            invite_keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    "🚀 Join Private Group · ቡድኑን ይቀላቀሉ",
                    url=enrollment.invite_link,
                )]]
            )
            await context.bot.send_message(
                chat_id=student_id,
                text=(
                    "🎉 <b>Payment verified — welcome to A+ Academy!</b>\n"
                    "🎉 <b>ክፍያዎ ተረጋግጧል — ወደ A+ አካዳሚ እንኳን በደህና መጡ!</b>\n\n"
                    "👉 Tap the button below to join your private class group:\n"
                    "👉 የግል ትምህርት ቡድንዎን ለመቀላቀል ከታች ያለውን ቁልፍ ይጫኑ፦\n\n"
                    f"{enrollment.invite_link}\n\n"
                    "🔒 This link works once — please do not share it.\n"
                    "🔒 ሊንኩ አንድ ጊዜ ብቻ ይሰራል — እባክዎ አያጋሩት።"
                ),
                parse_mode=ParseMode.HTML,
                reply_markup=invite_keyboard,
                disable_web_page_preview=True,
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


def build_app() -> Application:
    request = HTTPXRequest(
        connection_pool_size=16,
        connect_timeout=10,
        read_timeout=30,
        write_timeout=30,
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
            NAME: [
                MessageHandler(filters.COMMAND, fallback_text),
                MessageHandler(filters.TEXT & ~filters.COMMAND, payment_info),
                MessageHandler(~filters.TEXT, fallback_media),
            ],
            PAYMENT: [
                MessageHandler(filters.COMMAND, fallback_text),
                MessageHandler(filters.PHOTO, receive_payment),
                MessageHandler(filters.Document.IMAGE, receive_payment),
                MessageHandler(filters.Document.ALL, receive_payment),
                MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_text),
                MessageHandler(~filters.TEXT & ~filters.PHOTO & ~filters.Document.ALL, fallback_media),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("start", start),
            CommandHandler("help", help_cmd),
            MessageHandler(filters.ALL, fallback_text),
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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, catchall_message))
    app.add_handler(MessageHandler(~filters.TEXT, catchall_non_text))
    app.add_error_handler(on_error)
    return app


def main() -> None:
    threading.Thread(target=_start_health_server, daemon=True).start()
    app = build_app()
    logger.info("🤖 Bot is running...")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()