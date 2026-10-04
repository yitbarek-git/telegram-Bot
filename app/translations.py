"""
Translations module for A+ Academy Telegram Bot.
Plain-text safe strings for Ethiopian university freshman education bot.
"""

TRANSLATIONS = {
    "en": {
        "welcome": (
            "👋 Welcome to A+ Academy!\n\n"
            "The premier academic platform for Ethiopian university freshman students.\n\n"
            "Get complete freshman course tutorials, lecture PDFs, chapter video lessons, "
            "past mid & final exams with detailed solutions, and department preparation.\n\n"
            "Course Package Price: 400 ETB (Complete Freshman Year Access)\n\n"
            "Please choose an option below to continue:"
        ),
        "courses_overview": (
            "🎓 A+ Academy Freshman Education Package\n\n"
            "📚 Included Subjects:\n"
            "• Mathematics (Applied & Social)\n"
            "• Communicative English\n"
            "• General Physics\n"
            "• Critical Thinking & Logic\n"
            "• General Psychology\n"
            "• Economics\n"
            "• Introduction to Emerging Technologies\n"
            "• History of Ethiopia & the Horn\n"
            "• Anthropology\n"
            "• Physical Fitness\n"
            "• Computer Programming & Geography\n\n"
            "📦 What you receive:\n"
            "• Chapter-by-chapter video lectures\n"
            "• Short summary notes & PPT slides\n"
            "• Midterm exam collection with answers\n"
            "• Final exam worksheets and model questions\n"
            "• University department selection guidance\n\n"
            "💰 Full Package Price: 400 ETB (One-time payment)\n\n"
            "Click 'Payment / Enrollment' below to enroll."
        ),
        "payment_menu_text": (
            "💳 A+ Academy Enrollment (400 ETB)\n\n"
            "Pay exactly 400 ETB using Telebirr or local bank transfer (CBE), "
            "then send the payment receipt/screenshot here.\n\n"
            "Select your preferred payment method below:"
        ),
        "telebirr_instructions": (
            "📱 Telebirr Payment Instructions\n\n"
            "1. Open Telebirr app or dial *127#\n"
            "2. Send 400 ETB to:\n"
            "   • Phone Number: {phone}\n"
            "   • Account Name: {name}\n"
            "   • Amount: 400 ETB\n\n"
            "3. Take a screenshot of the completed payment confirmation.\n"
            "4. Send the screenshot here as a photo or image file."
        ),
        "cbe_instructions": (
            "🏦 CBE (Commercial Bank of Ethiopia) Instructions\n\n"
            "1. Open CBE Birr, CBE Mobile Banking, or visit a branch\n"
            "2. Transfer 400 ETB to:\n"
            "   • Account Number: {account}\n"
            "   • Account Name: {name}\n"
            "   • Amount: 400 ETB\n\n"
            "3. Take a screenshot or clear photo of the payment slip/SMS confirmation.\n"
            "4. Send the screenshot here as a photo or image file."
        ),
        "ask_receipt": (
            "📸 Submit Payment Screenshot\n\n"
            "Please send the exact payment receipt/screenshot as a photo or image file now.\n\n"
            "If you sent via Telebirr or CBE, send the screenshot showing the transaction details.\n"
            "Type /cancel to cancel."
        ),
        "receipt_received_pending": (
            "✅ Your payment receipt has been submitted. Please wait for admin approval.\n\n"
            "Receipt ID: #{payment_id}\n"
            "Status: Pending Verification\n\n"
            "Our admin team will review your receipt and activate your access shortly.\n"
            "Use the 'My Enrollment' button or /status to check anytime."
        ),
        "receipt_updated_pending": (
            "🔄 Updated receipt received! (Submission #{submission_count})\n\n"
            "Receipt ID: #{payment_id}\n"
            "Status: Pending Verification\n\n"
            "Our admin has been notified with your latest receipt."
        ),
        "approval_student_message": (
            "🎉 Congratulations! Your payment has been verified!\n\n"
            "Welcome to A+ Academy Freshman Batch!\n\n"
            "🔗 Your Private Telegram Group Link:\n{invite_link}\n\n"
            "Please click the link above to join your classmates and access all video lessons, "
            "lecture notes, and exam materials."
        ),
        "rejection_student_message": (
            "❌ Payment Not Approved\n\n"
            "Your submitted receipt could not be verified by the admin.\n\n"
            "Please verify your payment details and make sure the screenshot shows "
            "the 400 ETB transfer clearly.\n\n"
            "You can submit a corrected screenshot now or contact support."
        ),
        "unrelated_message": (
            "👋 I can help you enroll in A+ Academy courses.\n\n"
            "Please choose an option from the menu below:"
        ),
        "not_an_image": (
            "⚠️ Please send the payment receipt as a clear photo or image file (PNG/JPG).\n\n"
            "If you need help or wish to go back, tap Main Menu."
        ),
        "cancel_success": "Cancelled. Type /start anytime to return to the main menu.",
        "select_language": "🌐 Select your preferred language / ቋንቋዎን ይምረጡ:",
        "language_set": "✅ Language changed to English.",
        "help_text": (
            "ℹ️ How to enroll in A+ Academy:\n\n"
            "1. Tap 'Freshman Courses' to see what's included.\n"
            "2. Tap 'Payment / Enrollment' to get our Telebirr or CBE bank details.\n"
            "3. Transfer 400 ETB.\n"
            "4. Take a screenshot of the transfer confirmation.\n"
            "5. Send the screenshot directly in this chat.\n"
            "6. Admin will verify your receipt and send your private group invite link!\n\n"
            "Commands:\n"
            "• /start - Open main menu\n"
            "• /status - Check payment & enrollment status\n"
            "• /help - Show this guide\n"
            "• /cancel - Cancel current action"
        ),
    },
    "am": {
        "welcome": (
            "👋 እንኳን ወደ አፕላስ አካዳሚ (A+ Academy) በደህና መጡ!\n\n"
            "ለኢትዮጵያ ዩኒቨርሲቲ የፍሬሽማን ተማሪዎች የተዘጋጀ ቁጥር 1 የትምህርት መድረክ።\n\n"
            "የሁሉንም የፍሬሽማን ኮርሶች አጋዥ የቪዲዮ ትምህርቶች፣ ማጠቃለያ ማስታወሻዎች (PDFs)፣ "
            "የሚድተርም እና የፋይናል ፈተናዎች ከነሙሉ ማብራሪያቸው እና የዲፓርትመንት መረጃዎችን ያገኛሉ።\n\n"
            "የኮርሱ ዋጋ፦ 400 ብር (ለሙሉ የፍሬሽማን አመት)\n\n"
            "ለመቀጠል ከታች ካሉት አማራጮች አንዱን ይምረጡ፦"
        ),
        "courses_overview": (
            "🎓 የA+ Academy ፍሬሽማን የትምህርት ፓኬጅ\n\n"
            "📚 የሚያካትታቸው ኮርሶች፦\n"
            "• Mathematics (Applied & Social)\n"
            "• Communicative English\n"
            "• General Physics\n"
            "• Critical Thinking & Logic\n"
            "• General Psychology\n"
            "• Economics\n"
            "• Emerging Technologies\n"
            "• History of Ethiopia & the Horn\n"
            "• Anthropology\n"
            "• Physical Fitness\n"
            "• Computer Programming & Geography\n\n"
            "📦 የሚያገኙት ነገር፦\n"
            "• በየምዕራፉ የተዘጋጁ የቪዲዮ ማብራሪያዎች\n"
            "• አጫጭር የPDF ማጠቃለያ ኖቶች\n"
            "• ያለፉ አመታት የሚድተርም ፈተናዎች ከመፍትሄያቸው ጋር\n"
            "• የፋይናል ፈተና ጥያቄዎች እና ሞዴል ፈተናዎች\n"
            "• የዲፓርትመንት አመራረጥ መመሪያዎች\n\n"
            "💰 የፓኬጁ ዋጋ፦ 400 ብር ብቻ (የአንድ ጊዜ ክፍያ)\n\n"
            "ለመመዝገብ ከታች 'ክፍያ / ምዝገባ' የሚለውን ይጫኑ።"
        ),
        "payment_menu_text": (
            "💳 የA+ Academy ምዝገባ ክፍያ (400 ብር)\n\n"
            "በትክክል 400 ብር በቴሌብር (Telebirr) ወይም በኢትዮጵያ ንግድ ባንክ (CBE) ይክፈሉ፣ "
            "ከዚያም የከፈሉበትን ደረሰኝ/Screenshot እዚህ ይላኩ።\n\n"
            "የክፍያ ዘዴዎን ይምረጡ፦"
        ),
        "telebirr_instructions": (
            "📱 የቴሌብር (Telebirr) የክፍያ መመሪያ\n\n"
            "1. የቴሌብር መተግበሪያን ይክፈቱ ወይም *127# ይደውሉ\n"
            "2. 400 ብር ወደሚከተለው ቁጥር ያስተላልፉ፦\n"
            "   • ስልክ ቁጥር፦ {phone}\n"
            "   • የስም ማረጋገጫ፦ {name}\n"
            "   • መጠን፦ 400 ብር\n\n"
            "3. ክፍያው ሲጠናቀቅ የደረሰኙን Screenshot ያንሱ።\n"
            "4. ያነሱትን Screenshot እዚህ በፎቶ ወይም በምስል ፋይል ይላኩ።"
        ),
        "cbe_instructions": (
            "🏦 የኢትዮጵያ ንግድ ባንክ (CBE) የክፍያ መመሪያ\n\n"
            "1. በCBE Birr፣ በሞባይል ባንኪንግ ወይም በባንክ ቅርንጫፍ\n"
            "2. 400 ብር ወደሚከተለው ሂሳብ ያስተላልፉ፦\n"
            "   • የሂሳብ ቁጥር፦ {account}\n"
            "   • የስም ማረጋገጫ፦ {name}\n"
            "   • መጠን፦ 400 ብር\n\n"
            "3. የከፈሉበትን ደረሰኝ Screenshot ወይም የደረሰኙን ግልጽ ፎቶ ያንሱ።\n"
            "4. ያነሱትን Screenshot እዚህ በፎቶ ወይም በምስል ፋይል ይላኩ።"
        ),
        "ask_receipt": (
            "📸 የክፍያ ደረሰኝ (Screenshot) ይላኩ\n\n"
            "እባክዎ የከፈሉበትን ትክክለኛ ደረሰኝ በፎቶ ወይም በምስል ፋይል አሁን ይላኩ።\n\n"
            "በቴሌብር ወይም በንግድ ባንክ ያስተላለፉበትን ዝርዝር የሚያሳይ መሆን አለበት።\n"
            "ለማቋረጥ /cancel ይላኩ።"
        ),
        "receipt_received_pending": (
            "✅ የክፍያ ደረሰኝዎ ደርሶናል! እባክዎ የአስተዳዳሪውን ማረጋገጫ ይጠብቁ።\n\n"
            "የደረሰኝ መለያ፦ #{payment_id}\n"
            "ሁኔታ፦ በማረጋገጥ ላይ (Pending)\n\n"
            "አስተዳዳሪው ደረሰኙን ፈትሾ እንደጨረሰ የፕራይቬት ግሩፕ ሊንኩን ወዲያውኑ ይልክልዎታል።\n"
            "ሁኔታዎን ለመፈተሽ 'የእኔ ምዝገባ' የሚለውን ቁልፍ ወይም /status ይጠቀሙ።"
        ),
        "receipt_updated_pending": (
            "🔄 የተስተካከለ ደረሰኝ ደርሶናል! (ቅጽ #{submission_count})\n\n"
            "የደረሰኝ መለያ፦ #{payment_id}\n"
            "ሁኔታ፦ በማረጋገጥ ላይ (Pending)\n\n"
            "የቅርብ ጊዜው ደረሰኝ ለአስተዳዳሪው ተልኳል።"
        ),
        "approval_student_message": (
            "🎉 እንኳን ደስ አለዎት! ክፍያዎ ተረጋግጧል!\n\n"
            "እንኳን ወደ A+ Academy የፍሬሽማን ባች በደህና መጡ!\n\n"
            "🔗 የእርስዎ የፕራይቬት ቴሌግራም ግሩፕ ሊንክ፦\n{invite_link}\n\n"
            "የቪዲዮ ትምህርቶችን፣ ኖቶችን እና የፈተና ጥያቄዎችን ለማግኘት ሊንኩን ተጭነው ይቀላቀሉ።"
        ),
        "rejection_student_message": (
            "❌ ክፍያዎ አልተረጋገጠም\n\n"
            "የላኩት የክፍያ ደረሰኝ በአስተዳዳሪው ሊረጋገጥ አልቻለም።\n\n"
            "እባክዎ የከፈሉትን 400 ብር በትክክል የሚያሳይ ደረሰኝ መሆኑን አረጋግጠው "
            "ትክክለኛውን Screenshot አሁን ይላኩ ወይም አስተዳዳሪውን ያነጋግሩ።"
        ),
        "unrelated_message": (
            "👋 በA+ Academy ኮርሶች ለመመዝገብ ከታች ካሉት አማራጮች አንዱን ይምረጡ፦"
        ),
        "not_an_image": (
            "⚠️ እባክዎ የክፍያ ደረሰኙን እንደ ግልጽ ፎቶ ወይም የምስል ፋይል (PNG/JPG) ይላኩ።\n\n"
            "እገዛ ከፈለጉ ወይም ወደ ኋላ ለመመለስ 'ዋና ማውጫ' የሚለውን ይጫኑ።"
        ),
        "cancel_success": "ተሰርዟል። ወደ ዋና ማውጫ ለመመለስ በማንኛውም ጊዜ /start ይላኩ።",
        "select_language": "🌐 የመረጡትን ቋንቋ ይምረጡ / Select your preferred language:",
        "language_set": "✅ ቋንቋው ወደ አማርኛ ተቀይሯል።",
        "help_text": (
            "ℹ️ በA+ Academy እንዴት መመዝገብ ይቻላል?፦\n\n"
            "1. 'የፍሬሽማን ኮርሶች' የሚለውን ተጭነው የኮርሱን ዝርዝር ይመልከቱ።\n"
            "2. 'ክፍያ / ምዝገባ' የሚለውን ተጭነው የቴሌብር ወይም የንግድ ባንክ ሂሳብ ቁጥር ያግኙ።\n"
            "3. 400 ብር ያስተላልፉ።\n"
            "4. የከፈሉበትን ደረሰኝ Screenshot ያንሱ።\n"
            "5. ያነሱትን Screenshot እዚህ ይላኩ።\n"
            "6. አስተዳዳሪው ደረሰኙን አይቶ ሲያረጋግጥ የፕራይቬት ግሩፕ ሊንክ ይደርስዎታል!\n\n"
            "የትዕዛዞች ዝርዝር፦\n"
            "• /start - ዋናውን ማውጫ ለመክፈት\n"
            "• /status - የክፍያ እና የምዝገባ ሁኔታን ለማየት\n"
            "• /help - ይህን መመሪያ ለማየት\n"
            "• /cancel - ሂደቱን ለማቋረጥ"
        ),
    },
}


def t(key: str, lang: str = "en", **kwargs) -> str:
    """Retrieve text safely without throwing KeyError or format crashes."""
    selected_lang = lang if lang in TRANSLATIONS else "en"
    text = TRANSLATIONS[selected_lang].get(key) or TRANSLATIONS["en"].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
