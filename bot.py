import os
import logging
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler, CallbackQueryHandler
)
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
GROUP_ID = int(os.getenv("GROUP_ID"))   
TELEBIRR_NUMBER = "0929781996"
COURSE_PRICE = "400 ETB"

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

NAME, PAYMENT = range(2)
users_db = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "👋 Welcome to A+ Academy!\n"
        "Enroll in **All Freshman Courses** for a one-time payment.\n"
        "Please type your full name:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return NAME

async def payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        f"💵 Price: {COURSE_PRICE} (One-time for all courses)\n\n"
        f"💳 **Payment Instructions:**\n"
        f"1. Send {COURSE_PRICE} via Telebirr to: `{TELEBIRR_NUMBER}`\n"
        f"2. Take a screenshot of the successful transaction.\n\n"
        f"📸 Please upload the screenshot here now.",
        parse_mode="Markdown"
    )
    return PAYMENT

async def receive_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    if not update.message.photo:
        await update.message.reply_text("⚠️ Please send a screenshot of your payment.")
        return PAYMENT

    photo_file = update.message.photo[-1].file_id
    users_db[user.id] = {
        "name": context.user_data['name'],
        "course": "All Freshman Courses",
        "username": user.username
    }

    keyboard = [
        [InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}"),
         InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = (
        f"🚨 **New Enrollment Request**\n\n"
        f"👤 Name: {context.user_data['name']}\n"
        f"📚 Course: All Freshman Courses\n"
        f"🔗 Username: @{user.username if user.username else 'No Username'}\n"
        f"🆔 ID: `{user.id}`"
    )

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo_file,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

    await update.message.reply_text(
        "✅ Screenshot received! Admins are verifying your payment. "
        "You will receive your private group link shortly."
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Enrollment cancelled. Type /start to try again.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        return

    action, user_id_str = query.data.split('_')
    student_id = int(user_id_str)

    if action == "approve":
        try:
            invite_link = await context.bot.create_chat_invite_link(
                chat_id=GROUP_ID, member_limit=1
            )
            await context.bot.send_message(
                chat_id=student_id,
                text=(
                    "🎉 **Payment Verified!** Welcome to A+ Academy.\n\n"
                    f"Click the link below to join your private class group. "
                    "(Do not share this link, it only works once!)\n\n"
                    f"{invite_link.invite_link}"
                ),
                parse_mode="Markdown"
            )
            await query.edit_message_caption(
                caption=f"{query.message.caption}\n\n✅ **STATUS: APPROVED**",
                parse_mode="Markdown"
            )
        except Exception as e:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"Error generating link: {e}\n(Make sure the bot is an Admin in the group!)")
    elif action == "reject":
        await context.bot.send_message(
            chat_id=student_id,
            text=(
                "❌ **Payment Verification Failed.**\n\n"
                "We couldn't verify your screenshot. Please contact support or try again with /start."
            ),
            parse_mode="Markdown"
        )
        await query.edit_message_caption(
            caption=f"{query.message.caption}\n\n❌ **STATUS: REJECTED**",
            parse_mode="Markdown"
        )

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, payment_info)],
            PAYMENT: [MessageHandler(filters.PHOTO, receive_payment)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(admin_decision, pattern="^(approve|reject)_"))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()