import asyncio
import logging
import signal
import sys
from app.config import (
    BOT_TOKEN,
    ADMIN_IDS,
    ENABLE_HEALTH_SERVER,
    HOST,
    PORT,
)
from app.web import start_web_server

logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("aplus_bot")


async def main():
    logger.info("==========================================================")
    logger.info(" Starting A+ Academy Telegram Bot")
    logger.info("==========================================================")

    # 1. Start optional HTTP Health Server if enabled
    http_server = None
    if ENABLE_HEALTH_SERVER:
        http_server = start_web_server(host=HOST, port=PORT)
    else:
        logger.info("HTTP health server disabled via ENABLE_HEALTH_SERVER=false.")

    # 2. Validate BOT_TOKEN
    if not BOT_TOKEN:
        logger.error(
            "❌ BOT_TOKEN is not configured! Set it as an environment variable or in .env."
        )
        if http_server:
            logger.info("Health server remains active on port %d while configuring token.", PORT)
            stop_event = asyncio.Event()
            await stop_event.wait()
        return

    # 3. Build Telegram Application
    try:
        from app.bot import create_bot_app
    except ImportError as e:
        logger.error("Could not import telegram bot: %s. Run 'pip install -r requirements.txt'.", e)
        if http_server:
            stop_event = asyncio.Event()
            await stop_event.wait()
        return

    application = create_bot_app()

    # 4. Clean startup: Drop any leftover webhook to allow clean polling without 409 Conflict
    try:
        logger.info("Checking & clearing any existing Telegram webhook...")
        await application.bot.delete_webhook(drop_pending_updates=False)
        logger.info("Telegram webhook cleared. Polling mode ready.")
    except Exception as e:
        logger.warning("Notice on webhook check (will proceed with polling): %s", e)

    # 5. Graceful shutdown signals
    stop_event = asyncio.Event()

    def _signal_handler(signum, frame):
        sig_name = signal.Signals(signum).name if hasattr(signal, "Signals") else str(signum)
        logger.info("Received termination signal %s. Initiating graceful shutdown...", sig_name)
        stop_event.set()

    for sig in (getattr(signal, "SIGINT", None), getattr(signal, "SIGTERM", None)):
        if sig is not None:
            try:
                signal.signal(sig, _signal_handler)
            except (ValueError, AttributeError):
                pass

    # 6. Start Application & Long Polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling(
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=False,
    )
    logger.info("A+ Academy Bot is actively polling for Telegram updates.")

    # Notify admins on startup
    for admin_id in ADMIN_IDS:
        try:
            await application.bot.send_message(
                chat_id=admin_id,
                text="🚀 A+ Academy Telegram Bot is online!",
                parse_mode=None,
            )
        except Exception:
            pass

    # Wait for termination signal
    await stop_event.wait()

    # 7. Graceful Stop
    logger.info("Stopping Telegram application cleanly...")
    try:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        logger.info("Telegram bot shutdown completed.")
    except Exception as e:
        logger.error("Error during Telegram shutdown: %s", e)

    if http_server:
        try:
            http_server.shutdown()
            logger.info("Health server shutdown completed.")
        except Exception as e:
            logger.error("Error during HTTP server shutdown: %s", e)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Process exited.")
