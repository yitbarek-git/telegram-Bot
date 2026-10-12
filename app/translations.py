"""Translations module for A+ Academy Telegram Bot."""

TRANSLATIONS = {
    "en": {
        "start_language_prompt": (
            "🎓 A+ Academy\n\n"
            "Please choose your language / ቋንቋ ይምረጡ፦"
        ),
        "welcome": (
            "🎓 A+ Academy\n\n"
            "Welcome to A+ Academy!\n"
            "We provide learning resources and exam preparation materials "
            "for Ethiopian university freshman students.\n\n"
            "💵 Full-Year Access: 300 ETB (one-time payment)\n\n"
            "Choose an option below to get started:"
        ),
        "courses_overview": (
            "📚 Freshman Course \n\n"
            "Program: Complete Freshman Course\n"
            "Price: 300 ETB (one-time payment for the full academic year)\n\n"
            "Subjects Included:\n"
            "• Mathematics (Natural and Social Sciences)\n"
            "• Communicative English Skills I & II\n"
            "• General Physics\n"
            "• Logic and Critical Thinking\n"
            "• General Psychology\n"
            "• Economics\n"
            "• Emerging Technologies\n"
            "• History of Ethiopia and the Horn\n"
            "• Geography of Ethiopia and the Horn\n"
            "• Social Anthropology\n"
            "• Physical Fitness\n\n"
            "What You Get:\n"
            "• Video lessons\n"
            "• PDF summaries\n"
            "• Solved midterm and final exam questions\n\n"
            "⚠️ Note: Joining links are strictly personal. Sharing your private link "
            "or inviting unauthorized members will result in an immediate and permanent ban.\n\n"
            "Choose an option below:"
        ),
        "payment_menu_text": (
            "💳 Payment and Enrollment\n\n"
            "Amount: 300 ETB\n\n"
            "To enroll, transfer exactly 300 ETB using Telebirr or "
            "Commercial Bank of Ethiopia (CBE). Then send your payment "
            "receipt or screenshot here for verification.\n\n"
            "Choose your preferred payment method:"
        ),
        "telebirr_instructions": (
            "📱 Telebirr Payment Instructions\n\n"
            "Amount: 300 ETB\n"
            "Phone Number: {phone}\n"
            "Account Name: {name}\n\n"
            "How to Pay:\n"
            "1. Transfer exactly 300 ETB to the phone number above.\n"
            "2. Save a screenshot of the successful transaction.\n"
            "3. Send the screenshot here as a photo or image.\n\n"
            "Please make sure the payment details are clearly visible."
        ),
        "cbe_instructions": (
            "🏦 Commercial Bank of Ethiopia (CBE)\n\n"
            "Amount: 300 ETB\n"
            "Account Number: {account}\n"
            "Account Name: {name}\n\n"
            "How to Pay:\n"
            "1. Transfer exactly 300 ETB using CBE Birr, mobile banking, "
            "or a bank branch.\n"
            "2. Save a clear photo or screenshot of the transaction receipt.\n"
            "3. Send the receipt here as a photo or image.\n\n"
            "Please make sure the payment details are clearly visible."
        ),
        "ask_receipt": (
            "📸 Submit Your Payment Receipt\n\n"
            "Please send a clear photo or screenshot of your payment "
            "receipt now.\n\n"
            "Type /cancel if you want to cancel this step."
        ),
        "receipt_received_pending": (
            "✅ Payment Receipt Received\n\n"
            "Receipt ID: #{payment_id}\n"
            "Status: Awaiting Verification\n\n"
            "Your receipt has been received and is awaiting admin review. "
            "Please wait while your payment is verified.\n\n"
            "Once your payment is approved, you will receive an invitation "
            "link to the private Telegram group."
        ),
        "receipt_updated_pending": (
            "🔄 Updated Payment Receipt Received\n\n"
            "Receipt ID: #{payment_id} (Submission #{submission_count})\n"
            "Status: Awaiting Verification\n\n"
            "Your updated receipt has been received and sent for review. "
            "Please wait for the verification result."
        ),
        "approval_student_message": (
            "✅ Enrollment Confirmed!\n\n"
            "Your payment has been verified. Welcome to the A+ Academy "
            "Freshman Program!\n\n"
            "Your Private Telegram Group Link:\n"
            "{invite_link}\n\n"
            "🚨 WARNING:\n"
            "This invitation link is single-use and assigned uniquely to you. "
            "Do NOT forward or share this link with anyone. If you share this link, "
            "your access will be automatically revoked and you will be permanently "
            "banned from the group without a refund."
        ),
        "rejection_student_message": (
            "❌ Payment Verification Unsuccessful\n\n"
            "We couldn't verify your payment receipt.\n\n"
            "Please check that the receipt clearly shows the payment "
            "amount of 300 ETB and the transaction details. Then send "
            "a clear, valid receipt again."
        ),
        "unrelated_message": (
            "🎓 A+ Academy\n\n"
            "How can we help you?\n\n"
            "Choose an option below to explore our courses or enroll."
        ),
        "not_an_image": (
            "❌ Invalid File Format\n\n"
            "Please send your payment receipt as a clear photo or "
            "supported image file (PNG/JPG)."
        ),
        "cancel_success": (
            "Your action has been cancelled. "
            "Send /start at any time to return to the main menu."
        ),
        "select_language": (
            "🌐 Language Settings / የቋንቋ ምርጫ\n\n"
            "Please choose your language / ቋንቋ ይምረጡ፦"
        ),
        "language_set": "✅ Language changed to English.",
        "help_text": (
            "ℹ️ How to Enroll\n\n"
            "1. Select 'Freshman Courses' to view the course package.\n"
            "2. Select 'Payment / Enrollment' to view the payment details.\n"
            "3. Transfer exactly 300 ETB using Telebirr or CBE.\n"
            "4. Send your payment receipt here.\n"
            "5. Wait for admin verification. Once approved, you'll receive "
            "a link to the private Telegram group.\n\n"
            "⚠️ Policy Notice:\n"
            "Sharing private group access or invite links is strictly prohibited "
            "and results in an immediate account ban.\n\n"
            "Available Commands:\n"
            "• /start - Open the main menu\n"
            "• /status - Check your enrollment status\n"
            "• /help - View enrollment instructions\n"
            "• /cancel - Cancel the current action"
        ),
    },
    "am": {
        "start_language_prompt": (
            "🎓 A+ Academy\n\n"
            "እባክዎ ቋንቋ ይምረጡ / Please choose your language:"
        ),
        "welcome": (
            "🎓 A+ Academy\n\n"
            "እንኳን ወደ A+ Academy በደህና መጡ!\n"
            "ለኢትዮጵያ ዩኒቨርሲቲዎች የመጀመሪያ ዓመት (Freshman) ተማሪዎች "
            "የሚያስፈልጉ የትምህርትና የፈተና ዝግጅት ማቴሪያሎችን እናዘጋጃለን።\n\n"
            "💵 የሙሉ ዓመት አገልግሎት ክፍያ፦ 300 ብር (የአንድ ጊዜ ክፍያ)\n\n"
            "ለመቀጠል ከታች ካሉት አማራጮች አንዱን ይምረጡ፦"
        ),
        "courses_overview": (
            "📚 የFreshman ኮርሶች በሙሉ\n\n"
            "ፕሮግራም፦ የሙሉ Freshman ዓመት ኮርሶች\n"
            "ዋጋ፦ 300 ብር (ለሙሉ የትምህርት ዓመቱ የሚከፈል አንድ ጊዜ ብቻ)\n\n"
            "በፓኬጁ የሚካተቱ ትምህርቶች፦\n"
            "• Mathematics (Natural and Social Sciences)\n"
            "• Communicative English Skills I & II\n"
            "• General Physics\n"
            "• Logic and Critical Thinking\n"
            "• General Psychology\n"
            "• Economics\n"
            "• Emerging Technologies\n"
            "• History of Ethiopia and the Horn\n"
            "• Geography of Ethiopia and the Horn\n"
            "• Social Anthropology\n"
            "• Physical Fitness\n\n"
            "የሚያገኙት አገልግሎት፦\n"
            "• የቪዲዮ ትምህርቶች\n"
            "• የትምህርት ማጠቃለያ PDFዎች\n"
            "• የተሰሩ የMidterm እና Final ፈተናዎች ከነመፍትሔዎቻቸው\n\n"
        ),
        "payment_menu_text": (
            "💳 ክፍያና ምዝገባ\n\n"
            "የክፍያ መጠን፦ 300 ብር\n\n"
            "ለመመዝገብ ክፍያውን (300 ብር) በቴሌብር ወይም በኢትዮጵያ ንግድ "
            "ባንክ (CBE) ያስተላልፉ። በመቀጠል የክፍያ ደረሰኝ ወይም "
            "Screenshot እዚህ ይላኩ።\n\n"
            "የሚመችዎትን የክፍያ መንገድ ይምረጡ፦"
        ),
        "telebirr_instructions": (
            "📱 የቴሌብር ክፍያ መመሪያ\n\n"
            "የክፍያ መጠን፦ 300 ብር\n"
            "የስልክ ቁጥር፦ {phone}\n"
            "የሂሳብ ስም፦ {name}\n\n"
            "አከፋፈል፦\n"
            "1. 300 ብር ወደላይ በተጠቀሰው ስልክ ቁጥር ያስተላልፉ።\n"
            "2. ክፍያው መፈጸሙን የሚያሳይ Screenshot ያስቀምጡ።\n"
            "3. ምስሉን/Screenshot እዚህ ይላኩ።\n\n"
            "እባክዎ የክፍያው መረጃዎች በግልጽ መታየታቸውን ያረጋግጡ።"
        ),
        "cbe_instructions": (
            "🏦 የኢትዮጵያ ንግድ ባንክ (CBE) የክፍያ መመሪያ\n\n"
            "የክፍያ መጠን፦ 300 ብር\n"
            "የሂሳብ ቁጥር፦ {account}\n"
            "የሂሳብ ስም፦ {name}\n\n"
            "አከፋፈል፦\n"
            "1. በCBE Birr፣ በሞባይል ባንኪንግ ወይም በባንክ ቅርንጫፍ 300 ብር ያስተላልፉ።\n"
            "2. የክፍያ ደረሰኙን ግልጽ ፎቶ ወይም Screenshot ያስቀምጡ።\n"
            "3. ደረሰኙን እዚህ በፎቶ/ምስል መልክ ይላኩ።\n\n"
            "እባክዎ የክፍያው መረጃዎች በግልጽ መታየታቸውን ያረጋግጡ።"
        ),
        "ask_receipt": (
            "📸 የክፍያ ደረሰኝ ይላኩ\n\n"
            "እባክዎ የከፈሉበትን ደረሰኝ ግልጽ ፎቶ ወይም Screenshot አሁን ይላኩ።\n\n"
            "ሂደቱን ለማቋረጥ /cancel የሚለውን ይላኩ።"
        ),
        "receipt_received_pending": (
            "✅ የክፍያ ደረሰኝዎ ደርሶናል\n\n"
            "የደረሰኝ ID፦ #{payment_id}\n"
            "ሁኔታ፦ ማረጋገጥ ላይ\n\n"
            "የላኩት ደረሰኝ ደርሶናል። በአስተዳዳሪው እየተጣራ ስለሆነ "
            "እባክዎ የማረጋገጫ ውጤቱን በትዕግስት ይጠብቁ።\n\n"
            "ክፍያዎ ከተረጋገጠ በኋላ የቴሌግራም ቻናል/ግሩፕ መቀላቀያ ሊንክ ይላክልዎታል።"
        ),
        "receipt_updated_pending": (
            "🔄 አዲስ የክፍያ ደረሰኝ ደርሶናል\n\n"
            "የደረሰኝ ID፦ #{payment_id} (የማስገባት ሙከራ፦ #{submission_count})\n"
            "ሁኔታ፦ ማረጋገጥ ላይ\n\n"
            "የተሻሻለው ደረሰኝዎ ደርሶናል፤ ለማረጋገጥም ተልኳል። "
            "እባክዎ ውጤቱን ይጠብቁ።"
        ),
        "approval_student_message": (
            "✅ ምዝገባዎ ተረጋግጧል!\n\n"
            "ክፍያዎ ተረጋግጧል። እንኳን ወደ A+ Academy "
            "የFreshman ትምህርት ፕሮግራም በደህና መጡ!\n\n"
            "የቴሌግራም ግሩፕ መቀላቀያ ሊንክዎ፦\n"
            "{invite_link}\n\n"
            "🚨 ማስጠንቀቂያ ⚠ ፦\n"
            "ይህ ሊንክ ለርስዎ ብቻ የተዘጋጀ የመግቢያ ሊንክ ነው። "
            "ሊንኩን ለሌላ ሰው ማጋራት ወይም መላክ በጥብቅ የተከለከለ ነው። "
            "ሊንኩን ለሌላ ሰው አጋርተው ከተገኙ ያለ ምንም ማስ his ቅደሚያ ከግሩፑ በዘላቂነት "
            "(Permanently) የሚባረሩ ሲሆን ክፍያውም አይመለስልዎትም።"
        ),
        "rejection_student_message": (
            "❌ ክፍያዎ ሊረጋገጥ አልቻለም\n\n"
            "የላኩት የክፍያ ደረሰኝ ማረጋገጥ አልተቻለም።\n\n"
            "ደረሰኙ የተከፈለውን 300 ብር እና የግብይት መረጃዎችን በግልጽ "
            "ማሳየቱን ያረጋግጡ። በመቀጠል ትክክለኛና ግልጽ ደረሰኝ እንደገና ይላኩ።"
        ),
        "unrelated_message": (
            "🎓 A+ Academy\n\n"
            "ምን እንርዳዎት?\n\n"
            "የትምህርት ፓኬጆችን ለማየት ወይም ለመመዝገብ ከታች ካሉት አማራጮች ይምረጡ።"
        ),
        "not_an_image": (
            "❌ ያልተፈቀደ የፋይል ዓይነት\n\n"
            "እባክዎ የክፍያ ደረሰኝዎን በምስል/ፎቶ (PNG ወይም JPG) መልክ ይላኩ።"
        ),
        "cancel_success": (
            "ሂደቱ ተሰርዟል። ወደ ዋናው ማውጫ (Main Menu) ለመመለስ "
            "በማንኛውም ጊዜ /start ይላኩ።"
        ),
        "select_language": (
            "🌐 የቋንቋ ምርጫ / Language Settings\n\n"
            "እባክዎ ቋንቋ ይምረጡ / Please choose your language:"
        ),
        "language_set": "✅ ቋንቋው ወደ አማርኛ ተቀይሯል።",
        "help_text": (
            "ℹ️ የምዝገባ መመሪያ\n\n"
            "1. 'Freshman Courses' የሚለውን በመጫን የትምህርት ፓኬጁን ይመልከቱ።\n"
            "2. 'Payment / Enrollment' የሚለውን በመጫን የቴሌብር ወይም የCBE የክፍያ መረጃ ያግኙ።\n"
            "3. 300 ብር ክፍያ ይፈጽሙ።\n"
            "4. የክፍያ ደረሰኙን/Screenshot እዚህ ይላኩ።\n"
            "5. አስተዳዳሪው ክፍያዎን ካረጋገጠ በኋላ የግሩፕ መቀላቀያ ሊንክ ይደርስዎታል።\n\n"
            "⚠️ ደንብና መመሪያ፦\n"
            "የግሩፕ መግቢያ ሊንክ ለሌሎች ማጋራት በጥብቅ የተከለከለ ነው፤ ይህን ማድረግ ከግሩፕ ያባርራል።\n\n"
            "የትዕዛዝ ዝርዝር፦\n"
            "• /start - ወደ ዋናው ማውጫ ለመመለስ\n"
            "• /status - የምዝገባ ሁኔታን ለማየት\n"
            "• /help - የእገዛ መመሪያ ለማየት\n"
            "• /cancel - የተጀመረውን ሂደት ለማቋረጥ"
        ),
    },
}


def t(*args, **kwargs) -> str:
    """
    Flexible localized text helper.

    Supported calls:
        t("welcome", "en")
        t("welcome", "am")
        t("welcome", lang="en")
        t(user_dict, "welcome")
        t(user_obj, "welcome")
        t("en", "welcome")
        t("welcome", payment_id=101)
    """
    if len(args) == 0:
        return ""

    if len(args) == 1:
        lookup_key = args[0]
        lang = kwargs.pop("lang", "en") or "en"

    else:
        first, second = args[0], args[1]

        if isinstance(first, str) and first in TRANSLATIONS:
            lang = first
            lookup_key = second

        elif isinstance(second, str) and second in TRANSLATIONS:
            lookup_key = first
            lang = second

        elif isinstance(first, dict):
            lang = first.get("language") or "en"
            lookup_key = second

        elif hasattr(first, "language"):
            lang = getattr(first, "language", "en") or "en"
            lookup_key = second

        else:
            lookup_key = first
            lang = kwargs.pop("lang", "en") or "en"

    selected_lang = lang if lang in TRANSLATIONS else "en"

    text = (
        TRANSLATIONS[selected_lang].get(lookup_key)
        or TRANSLATIONS["en"].get(lookup_key, lookup_key)
    )

    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return text

    return text