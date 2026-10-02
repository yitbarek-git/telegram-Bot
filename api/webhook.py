import json
import logging
import asyncio
from http.server import BaseHTTPRequestHandler
from telegram import Update
from app.bot import create_bot_app
from app.config import WEBHOOK_SECRET

logger = logging.getLogger(__name__)

# Global cached bot application instance for serverless container reuse
_bot_app = None


def get_application():
    """Returns or initializes the Telegram Application instance."""
    global _bot_app
    if _bot_app is None:
        _bot_app = create_bot_app()
    return _bot_app


def run_async(coro):
    """Executes asynchronous coroutine within serverless request lifecycle."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coro)


async def process_telegram_update(update_dict: dict) -> None:
    """Processes an incoming Telegram webhook update."""
    app = get_application()
    if not app.running and not app._initialized:
        await app.initialize()

    update = Update.de_json(update_dict, app.bot)
    if update:
        await app.process_update(update)


class handler(BaseHTTPRequestHandler):
    """Vercel Serverless HTTP Handler for Telegram Webhook."""

    def _set_headers(self, status_code: int = 200, content_type: str = "application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def do_GET(self):
        """Health check endpoint."""
        self._set_headers(200)
        response = {
            "status": "healthy",
            "service": "A+ Academy Telegram Bot Webhook",
            "version": "2.0.0",
        }
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def do_POST(self):
        """Processes incoming Telegram webhook updates."""
        # Optional webhook secret verification
        if WEBHOOK_SECRET:
            token_header = self.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
            if token_header != WEBHOOK_SECRET:
                self._set_headers(403)
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
                return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length <= 0:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Empty body"}).encode("utf-8"))
            return

        body = self.rfile.read(content_length)

        try:
            update_data = json.loads(body.decode("utf-8"))
            run_async(process_telegram_update(update_data))
            self._set_headers(200)
            self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
        except Exception as e:
            logger.exception("Failed to process Telegram update: %s", e)
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": "Internal error"}).encode("utf-8"))
