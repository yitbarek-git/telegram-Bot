# A+ Academy Telegram Bot

A lightweight Telegram bot for **A+ Academy** course registration, payment verification, and private course access.

Built with **Python**, **python-telegram-bot**, and **JSON storage**. Designed to run on local machines, servers, VPSs, and cloud platforms.

## Features

* 🇬🇧 English & 🇪🇹 Amharic
* 📝 Student registration
* 📚 Course information
* 💳 Payment verification
* 📸 Receipt submission
* ✅ Admin approval
* 🔐 Private group access
* 💾 JSON-based storage
* ❤️ Optional health endpoint
* 🔄 Telegram long polling

## Project Structure

```text
telegram-Bot/
├── app/
│   ├── bot.py
│   ├── config.py
│   ├── storage.py
│   ├── translations.py
│   ├── web.py
│   ├── handlers/
│   └── keyboards/
├── data/
├── run.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup

```bash
git clone <REPO_URL>
cd telegram-Bot

python -m venv .venv
pip install -r requirements.txt
```

Configure your `.env` file using `.env.example`, then run:

```bash
python run.py
```

## Requirements

* Python 3.10+
* Telegram Bot Token
* Internet connection
* Persistent process
* Writable storage

## Configuration

```env
BOT_TOKEN=
ADMIN_IDS=
PRIVATE_GROUP_ID=
FALLBACK_GROUP_LINK=
DATA_DIR=data
COURSE_PRICE=
ENABLE_HEALTH_SERVER=true
PORT=3000
```

**Never commit `.env` or bot credentials to GitHub.**

## Admin Commands

```text
/stats
/pending
/student <TELEGRAM_ID>
```

## Tech Stack

**Python · python-telegram-bot · JSON · HTTP · dotenv**

---

### A+ Academy

**Learn. Build. Grow.**

**Developer:** Yitbarek K
