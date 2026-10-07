import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional
from app.config import HOST, PORT
from app.storage import get_admin_stats

logger = logging.getLogger(__name__)


class HealthStatusHandler(BaseHTTPRequestHandler):
    """Generic HTTP request handler for health checks and status inspection."""

    def _send_response_data(self, status_code: int, content: bytes, content_type: str = "text/plain"):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            msg = b"A+ Academy Bot is running."
            self._send_response_data(200, msg, "text/plain; charset=utf-8")
            return

        if self.path == "/health":
            try:
                stats = get_admin_stats()
                payload = {
                    "status": "healthy",
                    "service": "A+ Academy Telegram Bot",
                    "storage": "JSON",
                    "total_users": stats["total_users"],
                    "total_enrollments": stats["total_enrollments"],
                    "pending_payments": stats["pending_payments"],
                }
            except Exception:
                payload = {
                    "status": "healthy",
                    "service": "A+ Academy Telegram Bot",
                    "storage": "JSON",
                }
            data = json.dumps(payload).encode("utf-8")
            self._send_response_data(200, data, "application/json")
            return

        self._send_response_data(404, b"Not Found", "text/plain")

    def log_message(self, format, *args):
        # Silence routine HTTP polling logs to keep console clean
        pass


def start_web_server(host: str = HOST, port: int = PORT) -> Optional[HTTPServer]:
    """
    Starts a generic HTTP health check server in a background daemon thread.
    Catches bind errors gracefully without crashing the Telegram bot.
    """
    try:
        server = HTTPServer((host, port), HealthStatusHandler)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        logger.info("Health server listening on http://%s:%d", host, port)
        return server
    except Exception as e:
        logger.warning("Could not start optional HTTP health server on %s:%d (%s). Continuing Telegram bot.", host, port, e)
        return None
