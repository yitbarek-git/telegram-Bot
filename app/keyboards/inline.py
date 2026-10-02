from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.translations import t


def main_menu_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Returns the main interactive menu keyboard."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    t("btn_join_freshman", lang), callback_data="join_freshman"
                )
            ],
            [
                InlineKeyboardButton(
                    t("btn_language", lang), callback_data="change_language"
                )
            ],
            [
                InlineKeyboardButton(
                    t("btn_how_it_works", lang), callback_data="how_it_works"
                )
            ],
            [
                InlineKeyboardButton(
                    t("btn_support", lang), callback_data="support"
                )
            ],
            [
                InlineKeyboardButton(
                    t("btn_cancel", lang), callback_data="cancel_flow"
                )
            ],
        ]
    )


def language_selection_keyboard() -> InlineKeyboardMarkup:
    """Returns keyboard to switch languages."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🇬🇧 English", callback_data="set_lang:en"),
                InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="set_lang:am"),
            ],
            [
                InlineKeyboardButton("🔙 Back / ተመለስ", callback_data="back_to_menu")
            ],
        ]
    )


def approval_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    """
    Returns approval keyboard for admin.
    Callbacks strictly follow:
      approve_payment:PAYMENT_ID
      reject_payment:PAYMENT_ID
    """
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
