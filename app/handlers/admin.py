import logging
from app.config import ADMIN_IDS, FALLBACK_GROUP_LINK

try:
    from telegram import Update
    from telegram.ext import ContextTypes
except ImportError:
    Update = None
    ContextTypes = None

from app.translations import t
from app.storage import (
    get_payment_by_id,
    approve_payment,
    reject_payment,
    get_admin_stats,
    get_student_full_profile,
)

logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    """Verifies whether caller is an authorized admin in ADMIN_IDS."""
    return user_id in ADMIN_IDS and len(ADMIN_IDS) > 0


async def generate_group_invite_link(bot, chat_id: int, payment_id: int, student_id: int) -> str:
    """
    Generates a valid Telegram invite link for the private group with:
      - NO expiration date (expire_date=None)
      - NO member usage limit (member_limit=None)
      - creates_join_request=False
    If creation fails or chat_id is invalid, safely returns FALLBACK_GROUP_LINK.
    """
    if not chat_id:
        logger.info("PRIVATE_GROUP_ID not configured. Using fallback group link.")
        return FALLBACK_GROUP_LINK

    try:
        # Create an invite link with NO expiration and NO member limit
        invite = await bot.create_chat_invite_link(
            chat_id=chat_id,
            name=f"Student {student_id} (Pay #{payment_id})",
            expire_date=None,
            member_limit=None,
            creates_join_request=False,
        )
        if invite and getattr(invite, "invite_link", None):
            logger.info(
                "Successfully created permanent private group invite link for student %s: %s",
                student_id,
                invite.invite_link,
            )
            return invite.invite_link
    except Exception as e:
        logger.error(
            "Failed to generate Telegram invite link for chat_id %s (Error: %s). Falling back to %s",
            chat_id,
            e,
            FALLBACK_GROUP_LINK,
        )
        # Notify admins about group permission error
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=(
                        f"⚠️ Notice: Private group invite creation failed for chat ID {chat_id}.\n"
                        f"Telegram Error: {e}\n\n"
                        f"The bot safely used FALLBACK_GROUP_LINK: {FALLBACK_GROUP_LINK}\n\n"
                        "💡 To fix: Make sure the bot is an Administrator in the private group "
                        "with 'Invite Users via Link' permission."
                    ),
                    parse_mode=None,
                )
            except Exception:
                pass

    return FALLBACK_GROUP_LINK


async def admin_decision(update, context) -> None:
    """
    Handles payment approval/rejection callbacks from admin.
    Callbacks:
      approve_payment:PAYMENT_ID
      reject_payment:PAYMENT_ID
    Uses plain text to prevent Markdown parse entity errors on names/usernames.
    """
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.answer("⛔ Unauthorized: Admin access only.", show_alert=True)
        return

    data = query.data or ""
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
        msg = (query.message.caption or query.message.text or "") + "\n\n❌ Payment record not found in JSON storage."
        if query.message.photo or query.message.document:
            await query.edit_message_caption(caption=msg, parse_mode=None)
        else:
            await query.edit_message_text(text=msg, parse_mode=None)
        return

    student_telegram_id = payment["telegram_id"]
    student_lang = payment.get("language") or "en"
    existing_status = payment.get("status")

    try:
        if action == "approve_payment":
            if existing_status == "approved":
                await query.answer("⚠️ Payment has already been approved!", show_alert=True)
                msg = (query.message.caption or query.message.text or "") + f"\n\n✅ Already approved (Payment #{payment_id})."
                if query.message.photo or query.message.document:
                    await query.edit_message_caption(caption=msg, reply_markup=None, parse_mode=None)
                else:
                    await query.edit_message_text(text=msg, reply_markup=None, parse_mode=None)
                return

            from app.config import PRIVATE_GROUP_ID
            # 1. Generate permanent invite link (NO expiration, NO usage limit) or safe fallback
            invite_link = await generate_group_invite_link(
                bot=context.bot,
                chat_id=PRIVATE_GROUP_ID,
                payment_id=payment_id,
                student_id=student_telegram_id,
            )

            # 2. Record approval and exact working invite link in JSON storage
            res = approve_payment(payment_id=payment_id, invite_link=invite_link)
            if not res:
                await query.answer("Payment already processed.", show_alert=True)
                return

            # 3. Notify student with the valid invite link in their chosen language
            try:
                await context.bot.send_message(
                    chat_id=student_telegram_id,
                    text=t("approval_student_message", student_lang, invite_link=invite_link),
                    parse_mode=None,
                )
            except Exception as e:
                logger.error("Could not send approval message to student %s: %s", student_telegram_id, e)

            success_caption = (
                (query.message.caption or query.message.text or "")
                + f"\n\n✅ APPROVED by Admin\nInvite link provided: {invite_link}"
            )
            if query.message.photo or query.message.document:
                await query.edit_message_caption(
                    caption=success_caption,
                    reply_markup=None,
                    parse_mode=None,
                )
            else:
                await query.edit_message_text(
                    text=success_caption,
                    reply_markup=None,
                    parse_mode=None,
                )

        elif action == "reject_payment":
            if existing_status == "rejected":
                await query.answer("Payment already marked as rejected.", show_alert=True)
                return

            reject_payment(payment_id=payment_id)

            # Notify student in their chosen language
            try:
                await context.bot.send_message(
                    chat_id=student_telegram_id,
                    text=t("rejection_student_message", student_lang),
                    parse_mode=None,
                )
            except Exception as e:
                logger.error("Could not send rejection message to student %s: %s", student_telegram_id, e)

            rejection_caption = (
                (query.message.caption or query.message.text or "")
                + f"\n\n❌ REJECTED by Admin"
            )
            if query.message.photo or query.message.document:
                await query.edit_message_caption(
                    caption=rejection_caption,
                    reply_markup=None,
                    parse_mode=None,
                )
            else:
                await query.edit_message_text(
                    text=rejection_caption,
                    reply_markup=None,
                    parse_mode=None,
                )

    except Exception as e:
        logger.exception("Admin decision failed")
        await query.answer("Error processing request. Check logs.", show_alert=True)


async def stats_command(update, context) -> None:
    """Admin dashboard stats overview (plain text safe)."""
    if not is_admin(update.effective_user.id):
        return

    stats = get_admin_stats()
    pending_items = stats.get("pending_list", [])

    pending_lines = []
    for item in pending_items:
        pending_lines.append(
            f"• Payment #{item['payment_id']} | {item['full_name']} "
            f"({item['telegram_id']}) | Method: {item.get('payment_method', 'telebirr')}"
        )

    pending_section = (
        "\n".join(pending_lines) if pending_lines else "None (All caught up! 🎉)"
    )

    text = (
        "📊 A+ Academy Admin Statistics\n\n"
        f"👥 Total Registered Students: {stats['total_users']}\n"
        f"🎓 Active Enrollments: {stats['total_enrollments']}\n"
        f"⏳ Pending Payments: {stats['pending_payments']}\n"
        f"✅ Approved Payments: {stats['approved_payments']}\n"
        f"❌ Rejected Payments: {stats['rejected_payments']}\n\n"
        f"Recent Pending Submissions:\n{pending_section}\n\n"
        f"Lookup student info: /student <TELEGRAM_ID>"
    )

    await update.message.reply_text(text, parse_mode=None)


async def pending_command(update, context) -> None:
    """Quick lookup of all pending payments for admin."""
    if not is_admin(update.effective_user.id):
        return

    stats = get_admin_stats()
    pending_items = stats.get("pending_list", [])

    if not pending_items:
        await update.message.reply_text("✅ No pending payments found.", parse_mode=None)
        return

    lines = ["⏳ All Pending Payment Submissions:"]
    for item in pending_items:
        lines.append(
            f"• Payment #{item['payment_id']} | {item['full_name']} | "
            f"ID: {item['telegram_id']} | Method: {item.get('payment_method', 'telebirr')} | "
            f"Date: {item.get('created_at')}"
        )

    await update.message.reply_text("\n".join(lines), parse_mode=None)


async def student_lookup_command(update, context) -> None:
    """Lookup student customer record, enrollment, and payment history: /student <TELEGRAM_ID>"""
    if not is_admin(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: /student <TELEGRAM_ID>\nExample: /student 123456789",
            parse_mode=None,
        )
        return

    try:
        target_telegram_id = int(context.args[0].strip())
    except ValueError:
        await update.message.reply_text("Telegram ID must be an integer.", parse_mode=None)
        return

    profile = get_student_full_profile(target_telegram_id)
    if not profile or not profile.get("user"):
        await update.message.reply_text(
            f"No student record found for Telegram ID {target_telegram_id}.",
            parse_mode=None,
        )
        return

    u = profile["user"]
    enrollments = profile.get("enrollments", [])
    payments = profile.get("payments", [])

    lines = [
        "👤 Student Profile",
        f"• Name: {u.get('full_name', 'Student')}",
        f"• Telegram ID: {u.get('telegram_id')}",
        f"• Username: @{u.get('username') or 'None'}",
        f"• Language: {u.get('language')}",
        f"• Payment Status: {u.get('payment_status', 'none')}",
        f"• Access Status: {u.get('access_status', 'none')}",
        f"• Registered: {u.get('created_at')}",
        "",
        "🎓 Enrollment Status:",
    ]

    if enrollments:
        for e in enrollments:
            lines.append(
                f"• {e['course_title']} | Status: {e['status'].upper()} | Enrolled: {e.get('enrolled_at')}"
            )
            if e.get("invite_link"):
                lines.append(f"  Link: {e['invite_link']}")
    else:
        lines.append("• No active enrollments.")

    lines.append("")
    lines.append("💳 Payment History:")

    if payments:
        for p in payments:
            lines.append(
                f"• Payment #{p.get('id')} | Method: {p.get('payment_method', 'telebirr')} | "
                f"Status: {p.get('status', '').upper()} | Attempts: {p.get('submission_count', 1)} | "
                f"Date: {p.get('created_at')}"
            )
            if p.get("approved_at"):
                lines.append(f"  Approved at: {p['approved_at']}")
            elif p.get("rejected_at"):
                lines.append(f"  Rejected at: {p['rejected_at']}")
    else:
        lines.append("• No payment records found.")

    await update.message.reply_text("\n".join(lines), parse_mode=None)
