"""
Translations module for A+ Academy Telegram Bot.
Supports English ('en') and Amharic ('am').
"""

TRANSLATIONS = {
    "en": {
        "welcome": "👋 Welcome to *A+ Academy*!\n\nChoose an option below to get started:",
        "btn_join_freshman": "🎓 Join Freshman Course",
        "btn_how_it_works": "ℹ️ How it works",
        "btn_support": "🆘 Help/እገዛ",
        "btn_language": "🌐 Change Language / ቋንቋ",
        "btn_cancel": "✖ Cancel",
        "select_language": "🌐 Select your preferred language / ቋንቋዎን ይምረጡ:",
        "language_set": "✅ Language changed to *English*.",
        "enter_name": "📝 Send your *full name* exactly as you want it recorded.\nExample: *Amanuel Tadesse*",
        "name_too_short": "❌ Please enter a valid full name (at least 5 characters).\nExample: *Amanuel Tadesse*",
        "payment_instruction": (
            "💳 *Payment Instructions*\n\n"
            "{course_info}\n\n"
            "➡️ After payment, send the *screenshot* as a photo or image file.\n"
            "📸 Ready? Send your screenshot now."
        ),
        "course_info": (
            "📚 *Course:* {title}\n"
            "💰 *Price:* {price}\n"
            "📱 *Telebirr:* `{telebirr}`\n"
            "🏦 *CBE (ንግድ ባንክ):* `{cbe}`\n"
            "📦 *Includes:* {description}"
        ),
        "how_it_works": (
            "📖 *How it works*\n\n"
            "1️⃣ Send your full name\n"
            "2️⃣ Pay using Telebirr or CBE\n"
            "3️⃣ Send the payment screenshot\n"
            "4️⃣ Admin checks & verifies it\n"
            "5️⃣ You receive a private one-time group invite link\n\n"
            "{course_info}"
        ),
        "support": (
            "🆘 *Support*\n\n"
            "• First send your full name\n"
            "• Pay using the displayed Telebirr or CBE number\n"
            "• Send the payment screenshot as a photo or image file\n"
            "• If you send text or a sticker by mistake, just send the screenshot again\n"
            "• For additional issues, contact the admin."
        ),
        "cancel_success": "❌ Cancelled. Type /start when you are ready again.",
        "received_first": (
            "📸 *Screenshot received!*\n"
            "🧾 Payment ID: `#{payment_id}`\n\n"
            "The admin will verify your payment soon.\n"
            "Use /status to check your current state."
        ),
        "received_updated": (
            "🔄 *Updated screenshot received!*\n"
            "🧾 Payment ID: `#{payment_id}` (Submission #{submission_count})\n"
            "The admin has been notified with your latest receipt."
        ),
        "received_re_enrollment": (
            "🔄 *New payment screenshot received!*\n"
            "🧾 Payment ID: `#{payment_id}`\n"
            "It has been sent for admin verification."
        ),
        "not_an_image": (
            "❌ That file is not an image.\n\n"
            "Please send the payment screenshot as a *photo* or an *image file* (PNG, JPG)."
        ),
        "sticker_received": (
            "😕 I received a sticker.\n\n"
            "Please send your *payment screenshot* as a photo or image file."
        ),
        "text_received": (
            "📝 I received text, not a screenshot.\n\n"
            "Please send your *payment screenshot* as a photo or image file."
        ),
        "approval_message": (
            "✅ *Payment verified!*\n\n"
            "🎉 Welcome to *A+ Academy*!\n\n"
            "🔗 *Your private group link:*\n{invite_link}\n\n"
            "⚠️ *Note:* This link can only be used once."
        ),
        "rejection_message": (
            "❌ *Payment not approved*\n\n"
            "Your screenshot could not be verified by the admin.\n"
            "Please check your transaction details and try again with /start."
        ),
        "status_title": "📊 *Your Status*",
        "status_no_record": "📭 No record found yet.\nUse /start to begin enrollment.",
        "myinfo_title": "📋 *Your Information & History*",
        "help_text": (
            "🆘 *Help Guide*\n\n"
            "1️⃣ Type /start\n"
            "2️⃣ Send your full name\n"
            "3️⃣ Pay the displayed amount via Telebirr or CBE\n"
            "4️⃣ Send the screenshot (photo or image file)\n\n"
            "Commands:\n"
            "• /status - Check your payment & enrollment status\n"
            "• /myinfo - View your registered info & payment history\n"
            "• /cancel - Cancel the current action\n"
            "• /help - Show this help message"
        ),
        "unknown_error": "⚠️ An unexpected error occurred. Please try again later or contact the admin."
    },
    "am": {
        "welcome": "👋 እንኳን ወደ *አፕላስ አካዳሚ (A+ Academy)* በደህና መጡ!\n\nለመጀመር ከታች ካሉት አማራጮች አንዱን ይምረጡ፦",
        "btn_join_freshman": "🎓 የፍሬሽማን ኮርስ ተቀላቀል",
        "btn_how_it_works": "ℹ️ አሰራሩ እንዴት ነው?",
        "btn_support": "🆘 እገዛ/Help",
        "btn_language": "🌐 ቋንቋ ቀይር / Language",
        "btn_cancel": "✖ ሰርዝ",
        "select_language": "🌐 የመረጡትን ቋንቋ ይምረጡ / Select your preferred language:",
        "language_set": "✅ ቋንቋው ወደ *አማርኛ* ተቀይሯል።",
        "enter_name": "📝 እባክዎ *ሙሉ ስምዎን* በትክክል ይላኩ።\nምሳሌ፦ *አማኑኤል ታደሰ*",
        "name_too_short": "❌ እባክዎ ትክክለኛ ሙሉ ስም ያስገቡ (ቢያንስ 5 ፊደላት)።\nምሳሌ፦ *አማኑኤል ታደሰ*",
        "payment_instruction": (
            "💳 *የክፍያ መመሪያ*\n\n"
            "{course_info}\n\n"
            "➡️ ከከፈሉ በኋላ የከፈሉበትን *ደረሰኝ (Screenshot)* በፎቶ ወይም በምስል ፋይል ይላኩ።\n"
            "📸 ዝግጁ ነዎት? አሁኑኑ ደረሰኙን ይላኩ።"
        ),
        "course_info": (
            "📚 *ኮርስ:* {title}\n"
            "💰 *ዋጋ:* {price}\n"
            "📱 *ቴሌብር:* `{telebirr}`\n"
            "🏦 *ንግድ ባንክ (CBE):* `{cbe}`\n"
            "📦 *የሚያካትተው:* {description}"
        ),
        "how_it_works": (
            "📖 *አሰራሩ እንዴት ነው?*\n\n"
            "1️⃣ ሙሉ ስምዎን ይላኩ\n"
            "2️⃣ በቴሌብር ወይም በንግድ ባንክ ይክፈሉ\n"
            "3️⃣ የከፈሉበትን ደረሰኝ ይላኩ\n"
            "4️⃣ አስተዳዳሪው አረጋግጦ ይቀበላል\n"
            "5️⃣ የአንድ ጊዜ የፕራይቬት ግሩፕ ሊንክ ይደርስዎታል\n\n"
            "{course_info}"
        ),
        "support": (
            "🆘 *እገዛ*\n\n"
            "• መጀመሪያ ሙሉ ስምዎን ይላኩ\n"
            "• በተሰጠው የቴሌብር ወይም የንግድ ባንክ ሂሳብ ቁጥር ይክፈሉ\n"
            "• የክፍያ ደረሰኙን በፎቶ ወይም በምስል ፋይል ይላኩ\n"
            "• በስህተት ፅሁፍ ወይም ስቲከር ከላኩ ደረሰኙን በድጋሚ ይላኩ\n"
            "• ተጨማሪ ችግር ካጋጠመዎት አስተዳዳሪውን ያነጋግሩ።"
        ),
        "cancel_success": "❌ ተሰርዟል። ዝግጁ ሲሆኑ በድጋሚ /start ብለው ይጀምሩ።",
        "received_first": (
            "📸 *ደረሰኝዎ ደርሶናል!*\n"
            "🧾 የክፍያ መለያ፦ `#{payment_id}`\n\n"
            "አስተዳዳሪው በቅርቡ አረጋግጦ ሊንክ ይልክልዎታል።\n"
            "ሁኔታዎን ለመፈተሽ /status ይጠቀሙ።"
        ),
        "received_updated": (
            "🔄 *የተስተካከለ ደረሰኝ ደርሶናል!*\n"
            "🧾 የክፍያ መለያ፦ `#{payment_id}` (ቅጽ #{submission_count})\n"
            "የቅርብ ጊዜው ደረሰኝ ለአስተዳዳሪ ተልኳል።"
        ),
        "received_re_enrollment": (
            "🔄 *አዲስ የክፍያ ደረሰኝ ደርሶናል!*\n"
            "🧾 የክፍያ መለያ፦ `#{payment_id}`\n"
            "ለማረጋገጫ ለአስተዳዳሪ ተልኳል።"
        ),
        "not_an_image": (
            "❌ የተላከው ፋይል የምስል ፋይል አይደለም።\n\n"
            "እባክዎ የክፍያ ደረሰኙን እንደ *ፎቶ* ወይም እንደ ምስል ፋይል (PNG, JPG) ይላኩ።"
        ),
        "sticker_received": (
            "😕 ስቲከር ደርሶናል።\n\n"
            "እባክዎ የከፈሉበትን *ደረሰኝ* በፎቶ ወይም በምስል ፋይል ይላኩ።"
        ),
        "text_received": (
            "📝 የደረሰን ፅሁፍ ነው እንጂ ደረሰኝ አይደለም።\n\n"
            "እባክዎ የከፈሉበትን *ደረሰኝ* በፎቶ ወይም በምስል ፋይል ይላኩ።"
        ),
        "approval_message": (
            "✅ *ክፍያዎ ተረጋግጧል!*\n\n"
            "🎉 እንኳን ወደ *አፕላስ አካዳሚ* በደህና መጡ!\n\n"
            "🔗 *የፕራይቬት ግሩፕ ሊንክዎ:*\n{invite_link}\n\n"
            "⚠️ *ማሳሰቢያ:* ይህ ሊንክ ለአንድ ጊዜ ብቻ የሚያገለግል ነው።"
        ),
        "rejection_message": (
            "❌ *ክፍያዎ አልተረጋገጠም*\n\n"
            "የላኩት የክፍያ ደረሰኝ በአስተዳዳሪው ሊረጋገጥ አልቻለም።\n"
            "እባክዎ የግብይት ቁጥሩን በትክክል አረጋግጠው በ /start በድጋሚ ይሞክሩ።"
        ),
        "status_title": "📊 *የእርስዎ ሁኔታ*",
        "status_no_record": "📭 እስካሁን ምንም የተመዘገበ መረጃ አልተገኘም።\nለመመዝገብ /start ይላኩ።",
        "myinfo_title": "📋 *የእርስዎ መረጃ እና የክፍያ ታሪክ*",
        "help_text": (
            "🆘 *የእገዛ መመሪያ*\n\n"
            "1️⃣ /start ብለው ይላኩ\n"
            "2️⃣ ሙሉ ስምዎን ያስገቡ\n"
            "3️⃣ የተጠቀሰውን ክፍያ በቴሌብር ወይም በንግድ ባንክ ያስተላልፉ\n"
            "4️⃣ ደረሰኙን በፎቶ ወይም በምስል ፋይል ይላኩ\n\n"
            "የትዕዛዞች ዝርዝር፦\n"
            "• /status - የክፍያ/ምዝገባ ሁኔታን ለመፈተሽ\n"
            "• /myinfo - የገቡትን መረጃ እና የክፍያ ታሪክ ለማየት\n"
            "• /cancel - ሂደቱን ለማቋረጥ\n"
            "• /help - ይህን መመሪያ ለማየት"
        ),
        "unknown_error": "⚠️ ያልተጠበቀ ስህተት አጋጥሟል። እባክዎ ትንሽ ቆይተው እንደገና ይሞክሩ ወይም አስተዳዳሪውን ያነጋግሩ።"
    }
}


def t(key: str, lang: str = "en", **kwargs) -> str:
    """Get localized text with fallback to English."""
    selected_lang = lang if lang in TRANSLATIONS else "en"
    text = TRANSLATIONS[selected_lang].get(key) or TRANSLATIONS["en"].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
