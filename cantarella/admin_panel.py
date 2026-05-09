# Admin Panel - @Anonononononon
from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from database.db import db
from config import ADMINS
from datetime import date, timedelta
from logger import LOGGER

logger = LOGGER(__name__)

# Temporary storage for admin actions awaiting user input
admin_state = {}


def is_admin(user_id):
    return user_id in ADMINS


# ============================
# /admin - Main Admin Panel
# ============================
@Client.on_message(filters.command("admin") & filters.user(ADMINS) & filters.private)
async def admin_panel_cmd(client: Client, message: Message):
    await show_admin_panel(client, message)


async def show_admin_panel(client, message_or_query):
    total_users = await db.total_users_count()
    premium_cursor = await db.get_premium_users()
    premium_list = []
    async for u in premium_cursor:
        premium_list.append(u)
    premium_count = len(premium_list)

    text = (
        "<b>🛡 Admin Control Panel</b>\n\n"
        f"<b>👥 Total Users:</b> <code>{total_users}</code>\n"
        f"<b>💎 Premium Users:</b> <code>{premium_count}</code>\n\n"
        "<i>Select an option below:</i>"
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💎 Premium Manager", callback_data="ap_premium"),
            InlineKeyboardButton("👥 User Stats", callback_data="ap_stats")
        ],
        [
            InlineKeyboardButton("🚫 Ban User", callback_data="ap_ban"),
            InlineKeyboardButton("✅ Unban User", callback_data="ap_unban")
        ],
        [
            InlineKeyboardButton("📢 Broadcast", callback_data="ap_broadcast"),
            InlineKeyboardButton("📋 User List", callback_data="ap_userlist")
        ],
        [
            InlineKeyboardButton("💎 Premium List", callback_data="ap_premlist"),
            InlineKeyboardButton("🗑 Remove Premium", callback_data="ap_remprem")
        ],
        [InlineKeyboardButton("❌ Close", callback_data="ap_close")]
    ])

    if isinstance(message_or_query, Message):
        await message_or_query.reply_text(
            text, reply_markup=buttons, parse_mode=enums.ParseMode.HTML
        )
    elif isinstance(message_or_query, CallbackQuery):
        await message_or_query.edit_message_text(
            text, reply_markup=buttons, parse_mode=enums.ParseMode.HTML
        )


# ============================
# Premium Manager Sub-Panel
# ============================
@Client.on_callback_query(filters.regex("^ap_premium$"))
async def premium_manager(client: Client, cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        return await cb.answer("Not authorized", show_alert=True)

    text = (
        "<b>💎 Premium Manager</b>\n\n"
        "<b>Add Premium:</b>\n"
        "Send command: <code>/addprem USER_ID DAYS</code>\n"
        "<i>Use 0 for permanent premium</i>\n\n"
        "<b>Examples:</b>\n"
        "• <code>/addprem 123456 30</code> → 30 days\n"
        "• <code>/addprem 123456 0</code> → Lifetime\n\n"
        "<b>Remove Premium:</b>\n"
        "<code>/remprem USER_ID</code>"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 View Premium Users", callback_data="ap_premlist")],
        [InlineKeyboardButton("⬅️ Back to Panel", callback_data="ap_back")]
    ])

    await cb.edit_message_text(text, reply_markup=buttons, parse_mode=enums.ParseMode.HTML)


# ============================
# /addprem command
# ============================
@Client.on_message(filters.command("addprem") & filters.user(ADMINS) & filters.private)
async def add_premium_cmd(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text(
            "<b>Usage:</b> <code>/addprem USER_ID DAYS</code>\n"
            "<i>Use 0 for permanent</i>",
            parse_mode=enums.ParseMode.HTML
        )

    try:
        user_id = int(message.command[1])
        days = int(message.command[2])

        if days == 0:
            expiry_date = None
            duration_text = "Permanent (Lifetime)"
        else:
            expiry_date = (date.today() + timedelta(days=days)).isoformat()
            duration_text = f"{days} days (until {expiry_date})"

        await db.add_premium(user_id, expiry_date)

        await message.reply_text(
            f"<b>✅ Premium Activated!</b>\n\n"
            f"<b>👤 User ID:</b> <code>{user_id}</code>\n"
            f"<b>⏰ Duration:</b> {duration_text}\n\n"
            f"<i>User now has unlimited access.</i>",
            parse_mode=enums.ParseMode.HTML
        )

        try:
            await client.send_message(
                user_id,
                "<b>🎉 Congratulations!</b>\n\n"
                f"<b>Your Premium has been activated!</b>\n"
                f"<b>Duration:</b> {duration_text}\n\n"
                "<i>Enjoy unlimited downloads!</i>",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception:
            pass

    except ValueError:
        await message.reply_text("❌ User ID and Days must be numbers.")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


# ============================
# /remprem command
# ============================
@Client.on_message(filters.command("remprem") & filters.user(ADMINS) & filters.private)
async def remove_premium_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>Usage:</b> <code>/remprem USER_ID</code>",
            parse_mode=enums.ParseMode.HTML
        )

    try:
        user_id = int(message.command[1])
        await db.remove_premium(user_id)

        await message.reply_text(
            f"<b>✅ Premium Removed</b>\n\n"
            f"<b>👤 User ID:</b> <code>{user_id}</code>\n"
            f"<i>User is now on Free plan.</i>",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


# ============================
# User Stats
# ============================
@Client.on_callback_query(filters.regex("^ap_stats$"))
async def user_stats(client: Client, cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        return await cb.answer("Not authorized", show_alert=True)

    total = await db.total_users_count()
    premium_cursor = await db.get_premium_users()
    premium_count = 0
    async for _ in premium_cursor:
        premium_count += 1

    text = (
        "<b>📊 Bot Statistics</b>\n\n"
        f"<b>👥 Total Users:</b> <code>{total}</code>\n"
        f"<b>💎 Premium Users:</b> <code>{premium_count}</code>\n"
        f"<b>👤 Free Users:</b> <code>{total - premium_count}</code>\n"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back to Panel", callback_data="ap_back")]
    ])

    await cb.edit_message_text(text, reply_markup=buttons, parse_mode=enums.ParseMode.HTML)


# ============================
# Premium User List
# ============================
@Client.on_callback_query(filters.regex("^ap_premlist$"))
async def premium_list(client: Client, cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        return await cb.answer("Not authorized", show_alert=True)

    cursor = await db.get_premium_users()
    users = []
    async for u in cursor:
        uid = u.get('id', '?')
        name = u.get('name', 'Unknown')
        expiry = u.get('premium_expiry', 'Permanent')
        if expiry is None:
            expiry = 'Permanent'
        users.append(f"• <code>{uid}</code> - {name} (exp: {expiry})")

    if users:
        text = "<b>💎 Premium Users</b>\n\n" + "\n".join(users[:30])
        if len(users) > 30:
            text += f"\n\n<i>...and {len(users) - 30} more</i>"
    else:
        text = "<b>💎 Premium Users</b>\n\n<i>No premium users yet.</i>"

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back to Panel", callback_data="ap_back")]
    ])

    await cb.edit_message_text(text, reply_markup=buttons, parse_mode=enums.ParseMode.HTML)


# ============================
# Ban User
# ============================
@Client.on_callback_query(filters.regex("^ap_ban$"))
async def ban_prompt(client: Client, cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        return await cb.answer("Not authorized", show_alert=True)

    text = (
        "<b>🚫 Ban User</b>\n\n"
        "Send command:\n"
        "<code>/ban USER_ID</code>\n\n"
        "<i>User will be banned from using the bot.</i>"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back to Panel", callback_data="ap_back")]
    ])

    await cb.edit_message_text(text, reply_markup=buttons, parse_mode=enums.ParseMode.HTML)


# ============================
# Unban User
# ============================
@Client.on_callback_query(filters.regex("^ap_unban$"))
async def unban_prompt(client: Client, cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        return await cb.answer("Not authorized", show_alert=True)

    text = (
        "<b>✅ Unban User</b>\n\n"
        "Send command:\n"
        "<code>/unban USER_ID</code>\n\n"
        "<i>User will be unbanned and can use the bot again.</i>"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back to Panel", callback_data="ap_back")]
    ])

    await cb.edit_message_text(text, reply_markup=buttons, parse_mode=enums.ParseMode.HTML)


# ============================
# Broadcast prompt
# ============================
@Client.on_callback_query(filters.regex("^ap_broadcast$"))
async def broadcast_prompt(client: Client, cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        return await cb.answer("Not authorized", show_alert=True)

    text = (
        "<b>📢 Broadcast Message</b>\n\n"
        "To broadcast a message to all users:\n\n"
        "<b>1.</b> Send any message (text/photo/video/document)\n"
        "<b>2.</b> Reply to it with <code>/broadcast</code>\n\n"
        "<i>The message will be sent to all registered users.</i>"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back to Panel", callback_data="ap_back")]
    ])

    await cb.edit_message_text(text, reply_markup=buttons, parse_mode=enums.ParseMode.HTML)


# ============================
# User List
# ============================
@Client.on_callback_query(filters.regex("^ap_userlist$"))
async def user_list(client: Client, cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        return await cb.answer("Not authorized", show_alert=True)

    text = (
        "<b>📋 User List</b>\n\n"
        "Send command:\n"
        "<code>/users</code>\n\n"
        "<i>This will generate a JSON file with all registered users.</i>"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back to Panel", callback_data="ap_back")]
    ])

    await cb.edit_message_text(text, reply_markup=buttons, parse_mode=enums.ParseMode.HTML)


# ============================
# Remove Premium prompt
# ============================
@Client.on_callback_query(filters.regex("^ap_remprem$"))
async def remove_prem_prompt(client: Client, cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        return await cb.answer("Not authorized", show_alert=True)

    text = (
        "<b>🗑 Remove Premium</b>\n\n"
        "Send command:\n"
        "<code>/remprem USER_ID</code>\n\n"
        "<i>User will be downgraded to Free plan.</i>"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 View Premium Users", callback_data="ap_premlist")],
        [InlineKeyboardButton("⬅️ Back to Panel", callback_data="ap_back")]
    ])

    await cb.edit_message_text(text, reply_markup=buttons, parse_mode=enums.ParseMode.HTML)


# ============================
# Back to Panel
# ============================
@Client.on_callback_query(filters.regex("^ap_back$"))
async def back_to_panel(client: Client, cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        return await cb.answer("Not authorized", show_alert=True)

    total_users = await db.total_users_count()
    premium_cursor = await db.get_premium_users()
    premium_list = []
    async for u in premium_cursor:
        premium_list.append(u)
    premium_count = len(premium_list)

    text = (
        "<b>🛡 Admin Control Panel</b>\n\n"
        f"<b>👥 Total Users:</b> <code>{total_users}</code>\n"
        f"<b>💎 Premium Users:</b> <code>{premium_count}</code>\n\n"
        "<i>Select an option below:</i>"
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💎 Premium Manager", callback_data="ap_premium"),
            InlineKeyboardButton("👥 User Stats", callback_data="ap_stats")
        ],
        [
            InlineKeyboardButton("🚫 Ban User", callback_data="ap_ban"),
            InlineKeyboardButton("✅ Unban User", callback_data="ap_unban")
        ],
        [
            InlineKeyboardButton("📢 Broadcast", callback_data="ap_broadcast"),
            InlineKeyboardButton("📋 User List", callback_data="ap_userlist")
        ],
        [
            InlineKeyboardButton("💎 Premium List", callback_data="ap_premlist"),
            InlineKeyboardButton("🗑 Remove Premium", callback_data="ap_remprem")
        ],
        [InlineKeyboardButton("❌ Close", callback_data="ap_close")]
    ])

    await cb.edit_message_text(text, reply_markup=buttons, parse_mode=enums.ParseMode.HTML)


# ============================
# Close Panel
# ============================
@Client.on_callback_query(filters.regex("^ap_close$"))
async def close_panel(client: Client, cb: CallbackQuery):
    await cb.message.delete()
