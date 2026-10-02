import asyncio
import logging
import signal
import sys
from telegram.error import Conflict, NetworkError, TelegramError
from app.config import BOT_TOKEN, ADMIN_ID
from app.bot import create_bot_app
from app.database.queries import test_connection

logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("run_bot")


async def main():
    logger.info("==================================================")
    logger.info(" Starting A+ Academy Telegram Bot (Render Worker) ")
    logger.info("==================================================")

    if not BOT_TOKEN:
        logger.critical("BOT_TOKEN is not configured in environment variables.")
        sys.exit(1)

    # 1. Verify MySQL / Aiven connectivity
    logger.info("Testing MySQL Database Connection...")
    if test_connection():
        logger.info("✅ Successfully connected to MySQL database.")
    else:
        logger.warning(
            "⚠️ MySQL connection test failed or returned unhealthy. "
            "Please verify MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, and SSL settings."
        )

    # 2. Build Telegram Application
    application = create_bot_app()

    # 3. Clean startup: Drop any leftover webhook to prevent 409 Conflict
    try:
        logger.info("Clearing any existing Telegram webhook to allow clean long polling...")
        await application.bot.delete_webhook(drop_pending_updates=False)
        logger.info("✅ Webhook cleared successfully.")
    except Exception as e:
        logger.warning("Could not clear webhook during startup (will proceed): %s", e)

    # 4. Graceful shutdown registration
    stop_event = asyncio.Event()

    def _signal_handler(signum, frame):
        sig_name = signal.Signals(signum).name
        logger.info("Received termination signal %s. Initiating graceful shutdown...", sig_name)
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, _signal_handler)
        except (ValueError, AttributeError):
            pass

    # 5. Start Application & Long Polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling(
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=False,
    )
    logger.info("🚀 Bot is actively polling Telegram for updates...")

    # Notify admin on startup if configured
    if ADMIN_ID:
        try:
            await application.bot.send_message(
                chat_id=ADMIN_ID,
                text="🚀 *A+ Academy Bot is online on Render!*",
                parse_mode="Markdown",
            )
        except Exception:
            pass

    # Wait until termination signal is caught
    await stop_event.wait()

    # 6. Graceful Stop
    logger.info("Stopping polling and shutting down Telegram application...")
    try:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        logger.info("✅ Bot shutdown completed cleanly.")
    except Exception as e:
        logger.error("Error during application shutdown: %s", e)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot process exited.")
