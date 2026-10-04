# 🎓 A+ Academy Telegram Bot

A simple, reliable, free-deployable Telegram bot for **A+ Academy** university course registration, Telebirr/CBE payment verification, and private Telegram group access.

Built with **Python**, **JSON file storage** (zero external database required), and designed to deploy on the **Render Free Web Service** tier.

---

## 🌟 Key Features

- **Zero External Database**: No MySQL, Aiven, PostgreSQL, or Redis required. Everything is stored in local, atomic, auto-recovering JSON files (`data/users.json` and `data/payments.json`).
- **Render Free Web Service Ready**: Runs a lightweight background HTTP server on Render's `$PORT` responding to `GET /` and `GET /health` so Render keeps the service healthy, while the bot concurrently handles Telegram long polling.
- **A+ Academy Freshman Offer (400 ETB)**:
  - English, Mathematics, Logic, Psychology, Economics, Entrepreneurship, Physics, Anthropology, History, Computer Programming, Physical Fitness.
  - Video lessons, lecture PDFs, midterm exams, final exams, and department guidance.
- **Bilingual Support**: Fully localized in **English (🇬🇧)** and **Amharic (🇪🇹)**.
- **Safe Manual Payment Verification**:
  - Students submit screenshots (photo or document) or type transaction/reference numbers.
  - Status is set to `pending`.
  - Admins approve or reject submissions via inline Telegram buttons.
- **Private Telegram Group Invite Access**:
  - Upon approval, the bot automatically generates a single-use invite link (`member_limit=1`) to the private course group, or uses the configured fallback link (`https://t.me/+m6ikHXVS_ss0N2Vk`).
  - Access and enrollment details are persisted in JSON.

---

## 📁 Project Structure

```text
.
├── app/
│   ├── __init__.py
│   ├── bot.py                  # Telegram Application builder & handler registration
│   ├── config.py               # Clean environment variables & constants
│   ├── storage.py              # Thread-safe atomic JSON storage layer (users & payments)
│   ├── translations.py         # Bilingual text dictionaries (English & Amharic)
│   ├── web.py                  # Lightweight HTTP health check server for Render (GET / and /health)
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── common.py           # /start, /status, /myinfo, /help, /cancel, language switcher
│   │   ├── registration.py     # Name collection, Telebirr/CBE receipt & reference router
│   │   └── admin.py            # Approval/rejection callbacks, /stats, /pending, /student lookup
│   └── keyboards/
│       ├── __init__.py
│       └── inline.py           # Main interactive menu, language selector, approval keyboard
├── data/                       # Created automatically on first run
│   ├── users.json              # Registered students, access & enrollment status
│   └── payments.json           # Payment submissions & verification history
├── run.py                      # Main production entry point for Render Free Web Service
├── render.yaml                 # Render infrastructure-as-code blueprint
├── requirements.txt            # Minimal production dependencies
├── .env.example                # Example environment variables
├── .gitignore                  # Git ignore rules (protects data/*.json, .env, virtual environments)
└── README.md                   # This documentation
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

| Variable | Required | Description | Example |
| :--- | :---: | :--- | :--- |
| `BOT_TOKEN` | **Yes** | Telegram bot token from @BotFather | `7123456789:AAH...` |
| `ADMIN_IDS` | **Yes** | Comma-separated list of admin numeric Telegram IDs | `123456789,987654321` |
| `PRIVATE_GROUP_ID` | Optional | Telegram numeric ID of the private course group | `-100xxxxxxxxxx` |
| `FALLBACK_GROUP_LINK`| Optional | Fallback invite link if bot cannot generate single-use links | `https://t.me/+m6ikHXVS_ss0N2Vk` |
| `PORT` | Optional | Port for HTTP server (Render sets this automatically) | `3000` |

---

## 💻 Local Development

### 1. Create Virtual Environment & Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure `.env`
Set your `BOT_TOKEN`, `ADMIN_IDS`, and `PRIVATE_GROUP_ID` in `.env`.

### 3. Run the Bot
```bash
python run.py
```
This will:
1. Start the HTTP server on port `3000` (test via `http://localhost:3000/health`).
2. Automatically initialize `data/users.json` and `data/payments.json`.
3. Clear any old webhooks and start polling Telegram.

---

## 🚀 Render Free Web Service Deployment

### Step 1: Push Code to GitHub
```bash
git add .
git commit -m "feat: simplified A+ Academy bot with JSON storage for Render Free Web Service"
git push origin main
```

### Step 2: Create Web Service on Render
1. Open [Render Dashboard](https://dashboard.render.com).
2. Click **New +** ➔ **Web Service**.
3. Connect your GitHub repository.
4. Configure service details:
   - **Name**: `aplus-academy-bot`
   - **Region**: Oregon (or Frankfurt)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`
   - **Instance Type**: `Free`
5. Expand **Advanced**:
   - **Health Check Path**: `/health`

### Step 3: Add Environment Variables on Render
Under **Environment**, add:
- `BOT_TOKEN`: Your Telegram bot token from @BotFather.
- `ADMIN_IDS`: Your Telegram numeric user ID (e.g. `123456789`).
- `PRIVATE_GROUP_ID`: Your target course group ID (e.g. `-100xxxxxxxxxx`).
- `FALLBACK_GROUP_LINK`: `https://t.me/+m6ikHXVS_ss0N2Vk`

### Step 4: Deploy
Click **Create Web Service**. Render will install dependencies, launch `python run.py`, verify the `/health` endpoint, and start receiving student payments.

---

## 👥 Telegram Group Configuration & Permissions

To allow the bot to create one-time single-use invite links for approved students:
1. Add your bot to the private Telegram group: `https://t.me/+m6ikHXVS_ss0N2Vk`
2. Promote the bot to **Administrator**.
3. Enable the permission: **"Invite Users via Link"** (or "Add Members").
4. If the bot does not have permission or `PRIVATE_GROUP_ID` is unset, it will automatically send the fallback link `https://t.me/+m6ikHXVS_ss0N2Vk`.

---

## 🛠️ Admin Commands

- `/stats` - View total registered students, active enrollments, pending, approved, and rejected payments.
- `/pending` - View all pending submissions waiting for verification.
- `/student <TELEGRAM_ID>` - View complete profile, language, registration date, enrollment status, and payment history.
