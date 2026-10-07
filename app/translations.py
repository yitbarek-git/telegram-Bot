"""
Translations module for A+ Academy Telegram Bot.
Academic, clean, professional plain-text strings in English & Amharic.
"""

TRANSLATIONS = {
    "en": {
        "start_language_prompt": (
            "🎓 A+ Academy\n\n"
            "Choose your language / ቋንቋ ይምረጡ፦"
        ),
        "welcome": (
            "🎓 A+ Academy\n\n"
            "Welcome to A+ Academy Ethiopian university freshman education.\n\n"
            "Course Package: 400 ETB (Complete Year Access)\n\n"
            "Choose an option below:"
        ),
        "courses_overview": (
            "📚 Course Information\n\n"
            "Program: Freshman Complete Package\n"
            "Price: 400 ETB (One-time)\n\n"
            "Subjects Included:\n"
            "• Mathematics (Applied & Social)\n"
            "• Communicative English\n"
            "• General Physics\n"
            "• Critical Thinking & Logic\n"
            "• General Psychology\n"
            "• Economics\n"
            "• Emerging Technologies\n"
            "• History of Ethiopia & the Horn\n"
            "• Anthropology\n"
            "• Physical Fitness & Programming\n\n"
            "Includes: Video tutorials, summary PDFs, mid & final solved exams.\n\n"
            "Choose an option below:"
        ),
        "payment_menu_text": (
            "💳 Payment / Enrollment\n\n"
            "Amount: 400 ETB\n\n"
            "Pay exactly 400 ETB using Telebirr or CBE bank transfer, "
            "then send the payment receipt/screenshot here.\n\n"
            "Choose your payment method:"
        ),
        "telebirr_instructions": (
            "📱 Telebirr Payment Instructions\n\n"
            "Amount: 400 ETB\n"
            "Phone Number: {phone}\n"
            "Account Name: {name}\n\n"
            "Steps:\n"
            "1. Transfer 400 ETB to the number above.\n"
            "2. Take a screenshot of the completed confirmation.\n"
            "3. Send the screenshot here as a photo or image file."
        ),
        "cbe_instructions": (
            "🏦 CBE (Commercial Bank of Ethiopia) Instructions\n\n"
            "Amount: 400 ETB\n"
            "Account Number: {account}\n"
            "Account Name: {name}\n\n"
            "Steps:\n"
            "1. Transfer 400 ETB via CBE Birr, Mobile Banking, or branch.\n"
            "2. Take a clear screenshot/photo of the transaction slip.\n"
            "3. Send the screenshot here as a photo or image file."
        ),
        "ask_receipt": (
            "📸 Submit Payment Receipt\n\n"
            "Please send the exact payment screenshot/photo now.\n\n"
            "Type /cancel to cancel."
        ),
        "receipt_received_pending": (
            "✅ Payment Receipt Submitted\n\n"
            "Receipt ID: #{payment_id}\n"
            "Status: Pending Admin Review\n\n"
            "Your payment receipt has been submitted. Please wait for admin approval.\n"
            "You will receive your private group link once approved."
        ),
        "receipt_updated_pending": (
            "🔄 Updated Receipt Submitted\n\n"
            "Receipt ID: #{payment_id} (Submission #{submission_count})\n"
            "Status: Pending Admin Review\n\n"
            "The admin has been notified with your latest receipt."
        ),
        "approval_student_message": (
            "✅ Enrollment Approved\n\n"
            "Welcome to A+ Academy Freshman Batch!\n\n"
            "Your Private Telegram Group Link:\n{invite_link}\n\n"
            "Click the link above to join your group and access all course materials."
        ),
        "rejection_student_message": (
            "❌ Payment Not Approved\n\n"
            "Your submitted receipt could not be verified by the admin.\n\n"
            "Please check that the transfer shows 400 ETB clearly and send a valid screenshot."
        ),
        "unrelated_message": (
            "🎓 A+ Academy\n\n"
            "I can help you enroll in A+ Academy courses.\n\n"
            "Please choose an option below:"
        ),
        "not_an_image": (
            "❌ Invalid File Format\n\n"
            "Please send the receipt as a clear photo or image file (PNG/JPG)."
        ),
        "cancel_success": "Action cancelled. Type /start anytime to return to the main menu.",
        "select_language": (
            "🌐 Language Settings / የቋንቋ ምርጫ\n\n"
            "Choose your language / ቋንቋ ይምረጡ፦"
        ),
        "language_set": "✅ Language changed to English.",
        "help_text": (
            "ℹ️ How to Enroll\n\n"
            "1. Choose 'Freshman Courses' to view subjects.\n"
            "2. Choose 'Payment / Enrollment' for Telebirr or CBE details.\n"
            "3. Transfer 400 ETB.\n"
            "4. Send your payment screenshot here.\n"
            "5. Admin approves and sends your private group invite link.\n\n"
            "Commands:\n"
            "• /start - Main menu\n"
            "• /status - Check enrollment status\n"
            "• /help - Help guide\n"
            "• /cancel - Cancel current action"
        ),
    },
    "am": {
        "start_language_prompt": (
            "🎓 A+ Academy\n\n"
            "Choose your language / ቋንቋ ይምረጡ፦"
        ),
        "welcome": (
            "🎓 A+ Academy\n\n"
            "እንኳን ወደ አፕላስ አካዳሚ የፍሬሽማን ትምህርት በደህና መጡ።\n\n"
            "የፓኬጅ ዋጋ፦ 400 ETB (የሙሉ አመት ትምህርት)\n\n"
            "ከታች ካሉት አማራጮች አንዱን ይምረጡ፦"
        ),
        "courses_overview": (
            "📚 የኮርስ መረጃ\n\n"
            "ፕሮግራም፦ የፍሬሽማን ሙሉ ፓኬጅ\n"
            "ዋጋ፦ 400 ETB (የአንድ ጊዜ ክፍያ)\n\n"
            "የሚያካትታቸው ኮርሶች፦\n"
            "• Mathematics (Applied & Social)\n"
            "• Communicative English\n"
            "• General Physics\n"
            "• Critical Thinking & Logic\n"
            "• General Psychology\n"
            "• Economics\n"
            "• Emerging Technologies\n"
            "• History of Ethiopia & the Horn\n"
            "• Anthropology\n"
            "• Physical Fitness & Programming\n\n"
            "የሚያካትተው፦ የቪዲዮ ትምህርቶች፣ የPDF ማጠቃለያዎች፣ ያለፉ አመታት ፈተናዎች ከመፍትሄ ጋር።\n\n"
            "ከታች ካሉት አማራጮች አንዱን ይምረጡ፦"
        ),
        "payment_menu_text": (
            "💳 ክፍያ / ምዝገባ\n\n"
            "መጠን፦ 400 ETB\n\n"
            "በትክክል 400 ETB በቴሌብር ወይም በንግድ ባንክ (CBE) ይክፈሉ፣ "
            "ከዚያም የከፈሉበትን ደረሰኝ/Screenshot እዚህ ይላኩ።\n\n"
            "የክፍያ ዘዴዎን ይምረጡ፦"
        ),
        "telebirr_instructions": (
            "📱 የቴሌብር የክፍያ መመሪያ\n\n"
            "መጠን፦ 400 ETB\n"
            "ስልክ ቁጥር፦ {phone}\n"
            "የስም ማረጋገጫ፦ {name}\n\n"
            "ቅደም ተከተል፦\n"
            "1. 400 ETB ወደተጠቀሰው ቁጥር ያስተላልፉ።\n"
            "2. የተጠናቀቀውን ክፍያ Screenshot ያንሱ።\n"
            "3. ያነሱትን Screenshot እዚህ በፎቶ ወይም በምስል ፋይል ይላኩ።"
        ),
        "cbe_instructions": (
            "🏦 የኢትዮጵያ ንግድ ባንክ (CBE) መመሪያ\n\n"
            "መጠን፦ 400 ETB\n"
            "የሂሳብ ቁጥር፦ {account}\n"
            "የስም ማረጋገጫ፦ {name}\n\n"
            "ቅደም ተከተል፦\n"
            "1. በCBE Birr፣ በሞባይል ባንኪንግ ወይም በቅርንጫፍ 400 ETB ያስተላልፉ።\n"
            "2. የክፍያ ደረሰኙን ግልጽ Screenshot ወይም ፎቶ ያንሱ።\n"
            "3. ያነሱትን Screenshot እዚህ በፎቶ ወይም በምስል ፋይል ይላኩ።"
        ),
        "ask_receipt": (
            "📸 የክፍያ ደረሰኝ መላክ\n\n"
            "እባክዎ የከፈሉበትን ትክክለኛ ደረሰኝ በፎቶ ወይም በምስል ፋይል አሁን ይላኩ።\n\n"
            "ለማቋረጥ /cancel ይላኩ።"
        ),
        "receipt_received_pending": (
            "✅ የክፍያ ደረሰኝዎ ደርሶናል\n\n"
            "የደረሰኝ መለያ፦ #{payment_id}\n"
            "ሁኔታ፦ በማረጋገጥ ላይ (Pending)\n\n"
            "የክፍያ ደረሰኝዎ ደርሷል። እባክዎ የአስተዳዳሪውን ማረጋገጫ ይጠብቁ።\n"
            "ክፍያው እንደተረጋገጠ የፕራይቬት ግሩፕ ሊንክ ይደርስዎታል።"
        ),
        "receipt_updated_pending": (
            "🔄 የተስተካከለ ደረሰኝ ደርሶናል\n\n"
            "የደረሰኝ መለያ፦ #{payment_id} (ቅጽ #{submission_count})\n"
            "ሁኔታ፦ በማረጋገጥ ላይ (Pending)\n\n"
            "የቅርብ ጊዜው ደረሰኝ ለአስተዳዳሪው ተልኳል።"
        ),
        "approval_student_message": (
            "✅ ምዝገባዎ ተረጋግጧል\n\n"
            "እንኳን ወደ A+ Academy የፍሬሽማን ባች በደህና መጡ!\n\n"
            "የፕራይቬት ቴሌግራም ግሩፕ ሊንክዎ፦\n{invite_link}\n\n"
            "የቪዲዮ ትምህርቶችንና የፈተና ጥያቄዎችን ለማግኘት ሊንኩን ተጭነው ይቀላቀሉ።"
        ),
        "rejection_student_message": (
            "❌ ክፍያዎ አልተረጋገጠም\n\n"
            "የላኩት የክፍያ ደረሰኝ በአስተዳዳሪው ሊረጋገጥ አልቻለም።\n\n"
            "እባክዎ የከፈሉትን 400 ETB በትክክል የሚያሳይ ደረሰኝ መሆኑን አረጋግጠው በድጋሚ ይላኩ።"
        ),
        "unrelated_message": (
            "🎓 A+ Academy\n\n"
            "በA+ Academy ኮርሶች ለመመዝገብ ከታች ካሉት አማራጮች አንዱን ይምረጡ፦"
        ),
        "not_an_image": (
            "❌ የተሳሳተ የፋይል አይነት\n\n"
            "እባክዎ የክፍያ ደረሰኙን እንደ ግልጽ ፎቶ ወይም የምስል ፋይል (PNG/JPG) ይላኩ።"
        ),
        "cancel_success": "ተሰርዟል። ወደ ዋና ማውጫ ለመመለስ በማንኛውም ጊዜ /start ይላኩ።",
        "select_language": (
            "🌐 የቋንቋ ምርጫ / Language Settings\n\n"
            "ቋንቋ ይምረጡ / Choose your language፦"
        ),
        "language_set": "✅ ቋንቋው ወደ አማርኛ ተቀይሯል።",
        "help_text": (
            "ℹ️ የምዝገባ መመሪያ\n\n"
            "1. 'የፍሬሽማን ኮርሶች' የሚለውን ተጭነው ዝርዝሩን ይመልከቱ።\n"
            "2. 'ክፍያ / ምዝገባ' የሚለውን ተጭነው የቴሌብር ወይም የንግድ ባንክ ሂሳብ ያግኙ።\n"
            "3. 400 ETB ያስተላልፉ።\n"
            "4. የከፈሉበትን ደረሰኝ Screenshot እዚህ ይላኩ።\n"
            "5. አስተዳዳሪው ሲያረጋግጥ የፕራይቬት ግሩፕ ሊንክ ይደርስዎታል!\n\n"
            "የትዕዛዞች ዝርዝር፦\n"
            "• /start - ዋና ማውጫ\n"
            "• /status - የምዝገባ ሁኔታ\n"
            "• /help - መመሪያ\n"
            "• /cancel - ሂደቱን ማቋረጥ"
        ),
    },
}


def t(*args, **kwargs) -> str:
    """
    Flexible, rock-solid localized text helper.
    Supports all call signatures seamlessly:
      t("welcome", "en")
      t("welcome", "am")
      t("welcome", lang="en")
      t(user_dict, "welcome")
      t(user_obj, "welcome")
      t("en", "welcome")
      t("welcome", **kwargs)
    """
    if len(args) == 0:
        return ""

    if len(args) == 1:
        # e.g. t("welcome", lang="en", payment_id=101)
        lookup_key = args[0]
        lang = kwargs.pop("lang", "en") or "en"
    else:
        first, second = args[0], args[1]
        # Check if first is language string ("en" / "am")
        if isinstance(first, str) and first in TRANSLATIONS:
            lang = first
            lookup_key = second
        # Check if second is language string ("en" / "am")
        elif isinstance(second, str) and second in TRANSLATIONS:
            lookup_key = first
            lang = second
        # Check if first is a user object or dict: t(user, "welcome")
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
    text = TRANSLATIONS[selected_lang].get(lookup_key) or TRANSLATIONS["en"].get(lookup_key, lookup_key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
