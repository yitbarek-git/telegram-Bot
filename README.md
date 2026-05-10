🤖 Educational Enrollment Telegram Bot

Automates course enrollment, payment verification, and access control using a structured Telegram bot workflow.

📌 Features
Guided user flow (name → payment → submission)
Screenshot validation (image only)
Admin approval system (inline buttons)
Single-use private group invite links
Persistent user tracking (JSON storage)
Commands: /start, /status, /myinfo, /stats
⚙️ Tech Stack
Python
python-telegram-bot (async)
python-dotenv
JSON (lightweight database)


🚀 Setup
1. Install dependencies
pip install python-telegram-bot python-dotenv
2. Configure environment

Create .env file:

BOT_TOKEN=your_bot_token
ADMIN_ID=your_telegram_id
GROUP_ID=your_group_id
3. Run
python bot.py


🔄 Workflow
User
/start
Enter full name
Pay via Telebirr
Upload screenshot
Admin
Reviews submission
Approves or rejects
System sends access link automatically


📁 Data Storage
{
  "user_id": {
    "name": "string",
    "status": "pending | approved | rejected",
    "submission_count": 1
  }
}
🧠 What This Project Demonstrates
Stateful bot design (ConversationHandler)
Async event handling
Input validation and error control
Admin workflow automation
Access control using invite links


🤝 Collaboration
Contributions are welcome.

You can:

Improve validation and security
Add database integration
Extend to multi-course systems
Build admin dashboards

Open an issue or submit a pull request.


⭐ Support

If this project helps you:
⭐ Star the repository
🍴 Fork and build on it
📢 Share with others


📌 Future Improvements
Database integration (PostgreSQL)
Payment API automation
Admin dashboard
Multi-course support


👤 Author
Yitbarek
