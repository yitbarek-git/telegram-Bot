import logging
from telegram import Update
from telegram.ext import ContextTypes
from app.config import ADMIN_ID, GROUP_ID
from app.translations import t
from app.database.queries import (
    get_payment_by_id,
    approve_payment,
    reject_payment,
    get_admin_stats,
    get_student_full_profile,
)

logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    """Verifies whether caller is the authorized admin."""
    return user_id == ADMIN_ID and ADMIN_ID != 0


async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles payment approval/rejection callbacks from admin.
    Callbacks:
      approve_payment:PAYMENT_ID
      reject_payment:PAYMENT_ID
    """
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.answer("⛔ Unauthorized: Admin access only.", show_alert=True)
        return

    data = query.data
    if ":" not in data:
        return

    action, payment_id_str = data.split(":", 1)
    try:
        payment_id = int(payment_id_str)
    except ValueError:
        await query.answer("Invalid payment ID.", show_alert=True)
        return

    payment = get_payment_by_id(payment_id)
    if not payment:
        await query.edit_message_caption(
            caption=(query.message.caption or "") + "\n\n❌ Payment record not found.",
            parse_mode="Markdown",
        )
        return

    student_telegram_id = payment["telegram_id"]
    student_lang = payment.get("language") or "en"
    existing_status = payment.get("status")

    try:
        if action == "approve_payment":
            if existing_status == "approved":
                await query.edit_message_caption(
                    caption=(query.message.caption or "")
                    + f"\n\n✅ Payment #{payment_id} was already approved.",
                    parse_mode="Markdown",
                )
                return

            # Generate one-time Telegram invite link
            invite = await context.bot.create_chat_invite_link(
                chat_id=GROUP_ID,
                member_limit=1,
            )

            # Update MySQL payment to approved and record enrollment
            approve_payment(payment_id=payment_id, invite_link=invite.invite_link)

            # Notify student with invite link in their chosen language
            await context.bot.send_message(
                chat_id=student_telegram_id,
                text=t(
                    "approval_message",
                    student_lang,
                    invite_link=invite.invite_link,
                ),
                parse_mode="Markdown",
            )

            await query.edit_message_caption(
                caption=(query.message.caption or "")
                + f"\n\n✅ *APPROVED (Payment #{payment_id})*",
                reply_markup=None,
                parse_mode="Markdown",
            )

        elif action == "reject_payment":
            if existing_status == "rejected":
                await query.edit_message_caption(
                    caption=(query.message.caption or "")
                    + f"\n\n❌ Payment #{payment_id} was already rejected.",
                    parse_mode="Markdown",
                )
                return

            # Update MySQL payment to rejected
            reject_payment(payment_id=payment_id)

            # Notify student in their chosen language
            await context.bot.send_message(
                chat_id=student_telegram_id,
                text=t("rejection_message", student_lang),
                parse_mode="Markdown",
            )

            await query.edit_message_caption(
                caption=(query.message.caption or "")
                + f"\n\n❌ *REJECTED (Payment #{payment_id})*",
                reply_markup=None,
                parse_mode="Markdown",
            )

    except Exception as e:
        logger.exception("Admin decision failed")
        await query.answer("Error processing request. Check bot logs.", show_alert=True)
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"⚠️ Error while processing `{action}` for Payment `#{payment_id}`:\n`{e}`",
            parse_mode="Markdown",
        )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin dashboard stats overview."""
    if not is_admin(update.effective_user.id):
        return

    stats = get_admin_stats()
    pending_items = stats["pending_list"]

    pending_lines = []
    for item in pending_items:
        pending_lines.append(
            f"• Payment `#{item['payment_id']}` | {item['full_name']} "
            f"(`{item['telegram_id']}`) - {item['course_title']}"
        )

    pending_section = (
        "\n".join(pending_lines) if pending_lines else "None (All caught up! 🎉)"
    )

    text = (
        "📊 *A+ Academy Admin Statistics*\n\n"
        f"👥 *Total Registered Students:* {stats['total_users']}\n"
        f"🎓 *Active Enrollments:* {stats['total_enrollments']}\n"
        f"⏳ *Pending Payments:* {stats['pending_payments']}\n"
        f"✅ *Approved Payments:* {stats['approved_payments']}\n"
        f"❌ *Rejected Payments:* {stats['rejected_payments']}\n\n"
        f"*Recent Pending Submissions:*\n{pending_section}\n\n"
        f"💡 Lookup student info: `/student <TELEGRAM_ID>`"
    )

    await update.message.reply_text(text, parse_mode="Markdown")


async def pending_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Quick lookup of all pending payments for admin."""
    if not is_admin(update.effective_user.id):
        return

    stats = get_admin_stats()
    pending_items = stats["pending_list"]

    if not pending_items:
        await update.message.reply_text("✅ No pending payments found.", parse_mode="Markdown")
        return

    lines = ["⏳ *All Pending Payment Submissions:*"]
    for item in pending_items:
        lines.append(
            f"• *Payment #{item['payment_id']}* | {item['full_name']} | "
            f"ID: `{item['telegram_id']}` | Submissions: {item['submission_count']} | "
            f"Date: {item['created_at']}"
        )

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def student_lookup_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lookup student customer record, enrollment, and payment history: /student <TELEGRAM_ID>"""
    if not is_admin(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Usage: `/student <TELEGRAM_ID>`\nExample: `/student 123456789`",
            parse_mode="Markdown",
        )
        return

    try:
        target_telegram_id = int(context.args[0].strip())
    except ValueError:
        await update.message.reply_text("❌ Telegram ID must be an integer.", parse_mode="Markdown")
        return

    profile = get_student_full_profile(target_telegram_id)
    if not profile or not profile.get("user"):
        await update.message.reply_text(
            f"❌ No student record found for Telegram ID `{target_telegram_id}`.",
            parse_mode="Markdown",
        )
        return

    u = profile["user"]
    enrollments = profile.get("enrollments", [])
    payments = profile.get("payments", [])

    lines = [
        "👤 *Customer Profile*",
        f"• *Name:* {u['full_name']}",
        f"• *Telegram ID:* `{u['telegram_id']}`",
        f"• *Username:* @{u['username'] or 'None'}",
        f"• *Language:* {u['language']}",
        f"• *Registered:* {u['created_at']}",
        f"• *Last Updated:* {u['updated_at']}",
        "",
        "🎓 *Enrollment Status:*",
    ]

    if enrollments:
        for e in enrollments:
            lines.append(
                f"• {e['course_title']} | Status: *{e['status'].upper()}* | "
                f"Enrolled: {e['enrolled_at']}"
            )
            if e.get("invite_link"):
                lines.append(f"  Link: {e['invite_link']}")
    else:
        lines.append("• No active enrollments.")

    lines.append("")
    lines.append("💳 *Payment History:*")

    if payments:
        for p in payments:
            lines.append(
                f"• *Payment #{p['id']}* ({p['course_title']}) | Status: *{p['status'].upper()}* | "
                f"File: {p['file_type']} | Attempts: {p['submission_count']} | Date: {p['created_at']}"
            )
            if p.get("approved_at"):
                lines.append(f"  Approved at: {p['approved_at']}")
            elif p.get("rejected_at"):
                lines.append(f"  Rejected at: {p['rejected_at']}")
    else:
        lines.append("• No payment records found.")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
