import os
import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from app.config import PORT
from app.storage import get_admin_stats

logger = logging.getLogger(__name__)


class WebStatusHandler(BaseHTTPRequestHandler):
    """Lightweight HTTP request handler for Render Web Service health checks."""

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
                    "bot": "A+ Academy Telegram Bot",
                    "storage": "JSON",
                    "total_users": stats["total_users"],
                    "total_enrollments": stats["total_enrollments"],
                    "pending_payments": stats["pending_payments"],
                }
            except Exception:
                payload = {
                    "status": "healthy",
                    "bot": "A+ Academy Telegram Bot",
                    "storage": "JSON",
                }
            data = json.dumps(payload).encode("utf-8")
            self._send_response_data(200, data, "application/json")
            return

        self._send_response_data(404, b"Not Found", "text/plain")

    def log_message(self, format, *args):
        # Silence routine HTTP polling logs to keep console clean
        pass


def start_web_server(port: int = PORT) -> HTTPServer:
    """Starts the HTTP health check server in a background daemon thread."""
    server = HTTPServer(("0.0.0.0", port), WebStatusHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    logger.info("✅ Render Web Service HTTP server listening on port %d", port)
    return server
