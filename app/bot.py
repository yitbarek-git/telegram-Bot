import logging
from app.config import BOT_TOKEN

try:
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        CallbackQueryHandler,
        ConversationHandler,
        filters,
    )
except ImportError:
    Application = None

from app.handlers.common import (
    start,
    my_enrollment_command,
    switch_language_callback,
    help_command,
    cancel_command,
    get_group_id_command,
    error_handler,
)
from app.handlers.registration import (
    WAITING_RECEIPT,
    menu_callback_router,
    start_receipt_submission_command,
    receive_payment_media,
    direct_media_handler,
    fallback_unrelated_message,
)
from app.handlers.admin import (
    admin_decision,
    stats_command,
    pending_command,
    student_lookup_command,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def create_bot_app():
    """Builds and configures the Telegram Application instance."""
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set in environment or .env file.")

    application = Application.builder().token(BOT_TOKEN).build()

    # 1. Receipt submission conversation
    receipt_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(menu_callback_router, pattern="^submit_receipt$"),
            CommandHandler("pay", start_receipt_submission_command),
        ],
        states={
            WAITING_RECEIPT: [
                MessageHandler(filters.PHOTO | filters.Document.ALL, receive_payment_media),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_payment_media),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command),
            CommandHandler("start", start),
            CommandHandler("help", help_command),
        ],
        allow_reentry=True,
    )

    application.add_handler(receipt_conv)

    # 2. Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", my_enrollment_command))
    application.add_handler(CommandHandler("myinfo", my_enrollment_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CommandHandler("id", get_group_id_command))

    # 3. Interactive Menu Callbacks
    application.add_handler(
        CallbackQueryHandler(
            my_enrollment_command, pattern="^my_enrollment$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            switch_language_callback, pattern="^(change_language|set_lang:|start_lang:)"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            menu_callback_router,
            pattern="^(main_menu|view_courses|pay_menu|pay_method:telebirr|pay_method:cbe|help_menu)$",
        )
    )

    # 4. Admin Handlers
    application.add_handler(
        CallbackQueryHandler(admin_decision, pattern="^(approve_payment|reject_payment):")
    )
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("pending", pending_command))
    application.add_handler(CommandHandler("student", student_lookup_command))

    # 5. Direct media receipt uploads (if user sends photo directly without pressing menu button first)
    application.add_handler(
        MessageHandler(filters.PHOTO | filters.Document.ALL, direct_media_handler)
    )

    # 6. Fallback handler for any random or unrelated message (voice, video, sticker, random text)
    application.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, fallback_unrelated_message)
    )

    # 7. Global Error Handler
    application.add_error_handler(error_handler)

    return application
