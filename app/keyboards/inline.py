from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Returns the main interactive menu keyboard."""
    if lang == "am":
        return InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🎓 የፍሬሽማን ኮርሶች", callback_data="view_courses")],
                [InlineKeyboardButton("💳 ክፍያ / ምዝገባ (400 ETB)", callback_data="pay_menu")],
                [InlineKeyboardButton("📸 የከፈሉበትን ደረሰኝ ይላኩ", callback_data="submit_receipt")],
                [InlineKeyboardButton("📚 የእኔ ምዝገባ (Status)", callback_data="my_enrollment")],
                [
                    InlineKeyboardButton("ℹ️ እገዛ / መመሪያ", callback_data="help_menu"),
                    InlineKeyboardButton("🌐 ቋንቋ / Language", callback_data="change_language"),
                ],
            ]
        )
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎓 Freshman Courses", callback_data="view_courses")],
            [InlineKeyboardButton("💳 Payment / Enrollment (400 ETB)", callback_data="pay_menu")],
            [InlineKeyboardButton("📸 Submit Payment", callback_data="submit_receipt")],
            [InlineKeyboardButton("📚 My Enrollment", callback_data="my_enrollment")],
            [
                InlineKeyboardButton("ℹ️ Help", callback_data="help_menu"),
                InlineKeyboardButton("🌐 Language / ቋንቋ", callback_data="change_language"),
            ],
        ]
    )


def payment_methods_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Keyboard to choose between Telebirr and CBE Bank transfer."""
    if lang == "am":
        return InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📱 ቴሌብር (Telebirr)", callback_data="pay_method:telebirr")],
                [InlineKeyboardButton("🏦 የኢትዮጵያ ንግድ ባንክ (CBE)", callback_data="pay_method:cbe")],
                [InlineKeyboardButton("📸 የከፈልኩበትን ደረሰኝ መላክ እፈልጋለሁ", callback_data="submit_receipt")],
                [
                    InlineKeyboardButton("⬅️ ተመለስ", callback_data="main_menu"),
                    InlineKeyboardButton("🏠 ዋና ማውጫ", callback_data="main_menu"),
                ],
            ]
        )
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📱 Telebirr", callback_data="pay_method:telebirr")],
            [InlineKeyboardButton("🏦 Commercial Bank of Ethiopia (CBE)", callback_data="pay_method:cbe")],
            [InlineKeyboardButton("📸 I already paid, send receipt", callback_data="submit_receipt")],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="main_menu"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"),
            ],
        ]
    )


def post_instruction_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Keyboard shown under payment instructions."""
    if lang == "am":
        return InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📸 አሁን ደረሰኝ ላክ", callback_data="submit_receipt")],
                [
                    InlineKeyboardButton("⬅️ ተመለስ", callback_data="pay_menu"),
                    InlineKeyboardButton("🏠 ዋና ማውጫ", callback_data="main_menu"),
                ],
            ]
        )
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📸 Send Receipt Now", callback_data="submit_receipt")],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="pay_menu"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"),
            ],
        ]
    )


def back_to_main_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Simple Back & Main Menu buttons."""
    if lang == "am":
        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⬅️ ተመለስ", callback_data="main_menu"),
                    InlineKeyboardButton("🏠 ዋና ማውጫ", callback_data="main_menu"),
                ]
            ]
        )
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⬅️ Back", callback_data="main_menu"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"),
            ]
        ]
    )


def language_selection_keyboard() -> InlineKeyboardMarkup:
    """Keyboard to select language."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🇬🇧 English", callback_data="set_lang:en"),
                InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="set_lang:am"),
            ],
            [
                InlineKeyboardButton("🏠 Main Menu / ዋና ማውጫ", callback_data="main_menu")
            ],
        ]
    )


def approval_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    """Interactive approval buttons for admin."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Approve", callback_data=f"approve_payment:{payment_id}"
                ),
                InlineKeyboardButton(
                    "❌ Reject", callback_data=f"reject_payment:{payment_id}"
                ),
            ]
        ]
    )
