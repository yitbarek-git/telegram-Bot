import http.server
import socketserver
import json
import os
import sys

PORT = int(os.getenv("PORT", "3000"))
HOST = "0.0.0.0"

class BotStatusHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"healthy","bot":"A+ Academy Telegram Bot","storage":"JSON"}')
            return

        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A+ Academy Telegram Bot - Render Web Service</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #090d16;
            color: #f1f5f9;
            margin: 0;
            padding: 24px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            box-sizing: border-box;
        }
        .card {
            background-color: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 16px;
            max-width: 640px;
            width: 100%;
            padding: 32px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
        }
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background-color: rgba(16, 185, 129, 0.15);
            color: #10b981;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 16px;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .dot {
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
            display: inline-block;
        }
        h1 {
            margin: 0 0 8px 0;
            font-size: 24px;
            color: #ffffff;
        }
        p {
            color: #94a3b8;
            font-size: 14px;
            line-height: 1.6;
            margin: 0 0 20px 0;
        }
        .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 24px;
        }
        .info-item {
            background-color: #1e293b;
            padding: 14px;
            border-radius: 8px;
            border: 1px solid #334155;
        }
        .info-label {
            font-size: 12px;
            color: #64748b;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }
        .info-val {
            font-size: 14px;
            font-weight: 500;
            color: #e2e8f0;
            font-family: monospace;
        }
        .code-box {
            background-color: #020617;
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 16px;
            font-family: monospace;
            font-size: 13px;
            color: #38bdf8;
            overflow-x: auto;
            margin-bottom: 20px;
        }
        .footer {
            font-size: 12px;
            color: #64748b;
            text-align: center;
            border-top: 1px solid #1e293b;
            padding-top: 16px;
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="badge">
            <span class="dot"></span> Render Free Web Service Running
        </div>
        <h1>A+ Academy Telegram Bot</h1>
        <p>A+ Academy course registration bot with lightweight JSON storage and built-in HTTP health check endpoint for Render.</p>
        
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Storage</div>
                <div class="info-val">JSON (data/users.json)</div>
            </div>
            <div class="info-item">
                <div class="info-label">Offer</div>
                <div class="info-val">400 ETB (Freshman)</div>
            </div>
            <div class="info-item">
                <div class="info-label">Languages</div>
                <div class="info-val">English & Amharic</div>
            </div>
            <div class="info-item">
                <div class="info-label">Health Check</div>
                <div class="info-val">GET /health (HTTP 200)</div>
            </div>
        </div>

        <div class="info-label" style="margin-bottom: 8px;">Start Command:</div>
        <div class="code-box">python run.py</div>

        <div class="footer">
            A+ Academy • Telegram Bot • JSON Storage
        </div>
    </div>
</body>
</html>"""
            self.wfile.write(html.encode("utf-8"))
            return

        super().do_GET()

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), BotStatusHandler) as httpd:
        print(f"Dev server listening on http://{HOST}:{PORT}", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    run_server()
