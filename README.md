# 🎓 A+ Academy Telegram Bot — Render Deployment Guide

Production-ready Telegram bot for **A+ Academy** course registration, Telebirr/CBE payment receipt verification, remote **Aiven MySQL** database persistence, bilingual support (English 🇬🇧 & Amharic 🇪🇹), and continuous **Render Background Worker (Long Polling)** deployment.

---

## 📁 Project Structure

```
.
├── app/
│   ├── bot.py                  # Telegram Application builder & handler registration
│   ├── config.py               # Environment configuration loader (MySQL, Telegram, admin)
│   ├── translations.py         # Bilingual dictionary (English 🇬🇧 & Amharic 🇪🇹)
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py       # PyMySQL connection context manager with Aiven SSL/TLS support
│   │   └── queries.py          # Parameterized SQL queries for users, payments, enrollments
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── common.py           # /start, /status, /myinfo, /help, /cancel, /id, language switcher
│   │   ├── registration.py     # Student name input & payment screenshot router
│   │   └── admin.py            # Payment approval/rejection, /stats, /pending, /student
│   └── keyboards/
│       ├── __init__.py
│       └── inline.py           # Menus, language selector & approve_payment:ID buttons
├── sql/
│   └── schema.sql              # MySQL DDL (users, courses, payments, enrollments) & freshman course seed
├── run.py                      # Production entry point for Render Background Worker
├── render.yaml                 # Render infrastructure-as-code blueprint
├── migrate_json_to_mysql.py    # Migration script for existing users.json data to MySQL
├── requirements.txt            # Python dependencies (python-telegram-bot, pymysql, cryptography, python-dotenv)
├── .env.example                # Example environment variables
├── .gitignore                  # Git ignore rules (.env, venv, secrets, logs)
└── README.md                   # Complete deployment & operational guide
```

---

## 🏗️ Architecture Decision: Render Background Worker vs. Webhook

| Feature | Render Web Service (Webhook) | Render Background Worker (Long Polling) | Decision |
| :--- | :--- | :--- | :--- |
| **HTTP Server Requirement** | Requires an HTTP server port, SSL routing, and certificate sync | No open web ports or ingress routing needed | **Worker Wins** |
| **Telegram Setup** | Requires calling `setWebhook` API with external domain + secret | Automatic via `delete_webhook` + `getUpdates` | **Worker Wins** |
| **Idle Behavior** | Web service free tier spins down after 15 min inactivity | Background worker runs continuously | **Worker Wins** |
| **Payment Flow** | High latency or cold boot timeouts on student screenshot upload | Instant processing with zero cold boots | **Worker Wins** |
| **Verdict** | Complex, prone to timeout & webhook desync | **Selected Architecture: Render Background Worker** | 🏆 **Winner** |

---

## 🚀 Render Deployment Instructions

### 1. Create the Render Background Worker
1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** ➔ **Background Worker**.
3. Connect your GitHub repository.
4. Fill in the settings:
   - **Name**: `aplus-academy-bot`
   - **Region**: Oregon (or nearest to your Aiven MySQL region)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`
   - **Plan**: Starter (or Worker plan)

### 2. Configure Environment Variables on Render
Under the **Environment** tab of your worker, add the following variables:

| Variable Name | Example Value | Description |
| :--- | :--- | :--- |
| `BOT_TOKEN` | `7123456789:AAH...` | Telegram bot token from @BotFather |
| `ADMIN_ID` | `123456789` | Admin numeric Telegram ID for approval receipts |
| `GROUP_ID` | `-1001234567890` | Numeric ID of the private Telegram course group |
| `MYSQL_HOST` | `mysql-xxxx.aivencloud.com` | Hostname from Aiven MySQL Service Overview |
| `MYSQL_PORT` | `12345` | Port from Aiven MySQL Service Overview |
| `MYSQL_USER` | `avnadmin` | MySQL username (default: `avnadmin`) |
| `MYSQL_PASSWORD` | `your_aiven_password` | MySQL password from Aiven |
| `MYSQL_DATABASE` | `defaultdb` | Target database name |
| `MYSQL_SSL_MODE` | `REQUIRED` | Enforces SSL/TLS for Aiven MySQL |

---

## 🗄️ Aiven MySQL Setup & Schema Import

### Step 1: Locate Aiven Credentials
In your [Aiven Console](https://console.aiven.io):
1. Select your MySQL service.
2. Under the **Overview** tab, copy:
   - **Host** (e.g. `mysql-24c16d56-myproject.aivencloud.com`)
   - **Port** (e.g. `23456`)
   - **User** (`avnadmin`)
   - **Password**
   - **Database** (`defaultdb`)

### Step 2: Import `sql/schema.sql` into Aiven
Run the following command from your terminal:
```bash
mysql -h <MYSQL_HOST> -P <MYSQL_PORT> -u <MYSQL_USER> -p <MYSQL_DATABASE> --ssl-mode=REQUIRED < sql/schema.sql
```
*Alternatively, you can open the Aiven Web Query Editor / DBeaver / MySQL Workbench and execute the contents of `sql/schema.sql`.*

### Step 3: Seed Data Explanation
The `sql/schema.sql` file includes the schema definition as well as seed data for the **Freshman Course**:
- **Price**: `400 ETB`
- **Telebirr**: `0929781996`
- **CBE Account**: `1000316427735`

This seed data uses `INSERT ... ON DUPLICATE KEY UPDATE`, making it idempotent and safe to re-run anytime.

---

## 📲 Telegram Post-Deployment Check
`run.py` automatically removes any old webhook before starting long polling. You do not need to manually delete the webhook. However, if you want to inspect or test via cURL:

- Check webhook status:
  ```bash
  curl https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo
  ```
- Send `/start` to your bot in Telegram to verify it responds immediately.
