import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)
from app.config import BOT_TOKEN
from app.handlers.common import (
    start,
    switch_language_callback,
    status_command,
    myinfo_command,
    help_command,
    cancel_command,
    get_group_id_command,
    error_handler,
)
from app.handlers.registration import (
    CHOICE,
    NAME,
    PAYMENT,
    menu_action,
    receive_student_name,
    payment_stage_router,
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


def create_bot_app() -> Application:
    """Builds and configures the Telegram Application instance."""
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set in environment or .env file.")

    application = Application.builder().token(BOT_TOKEN).build()

    # Main student registration conversation flow
    registration_conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(menu_action, pattern="^join_freshman$"),
        ],
        states={
            CHOICE: [
                CallbackQueryHandler(
                    menu_action,
                    pattern="^(join_freshman|how_it_works|support|cancel_flow)$",
                ),
                CallbackQueryHandler(
                    switch_language_callback,
                    pattern="^(change_language|set_lang:|back_to_menu)",
                ),
            ],
            NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_student_name),
                CommandHandler("cancel", cancel_command),
            ],
            PAYMENT: [
                MessageHandler(filters.ALL, payment_stage_router),
                CommandHandler("cancel", cancel_command),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command),
            CommandHandler("help", help_command),
            CommandHandler("start", start),
        ],
        allow_reentry=True,
    )

    # Register handlers
    application.add_handler(registration_conv)
    application.add_handler(
        CallbackQueryHandler(
            switch_language_callback, pattern="^(change_language|set_lang:|back_to_menu)"
        )
    )
    application.add_handler(
        CallbackQueryHandler(admin_decision, pattern="^(approve_payment|reject_payment):")
    )
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("myinfo", myinfo_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CommandHandler("id", get_group_id_command))

    # Admin Handlers
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("pending", pending_command))
    application.add_handler(CommandHandler("student", student_lookup_command))

    # Global Error Handler
    application.add_error_handler(error_handler)

    return application


def main():
    """Starts the bot with polling for local development."""
    logger.info("Initializing A+ Academy Telegram Bot in Polling Mode...")
    app = create_bot_app()
    logger.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=False)


if __name__ == "__main__":
    main()
