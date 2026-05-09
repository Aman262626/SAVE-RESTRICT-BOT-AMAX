# cantarella
# Don't Remove Credit
# Telegram Channel @cantarellabots

from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from database.db import db
from config import ADMINS, DB_URI
from datetime import date, timedelta
from logger import LOGGER

logger = LOGGER(__name__)

# State storage for multi-step admin actions
ADMIN_STATE = {}


# ======================================================
# /admin - Main Admin Panel
# ======================================================

@Client.on_message(filters.command("admin") & filters.user(ADMINS) & filters.private)
async def admin_panel(client: Client, message: Message):
    await show_admin_panel(client, message)


async def show_admin_panel(client, message_or_query):
    total_users = await db.total_users_count()
    premium_cursor = await db.get_premium_users()
    premium_count = 0
    async for _ in premium_cursor:
        premium_count += 1

    text = (
        "<b>🛡 Admin Control Panel</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>👥 Total Users:</b> <code>{total_users}</code>\n"
        f"<b>💎 Premium Users:</b> <code>{premium_count}</code>\n\n"
        "<i>Select an option below to manage the bot:</i>"
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👑 Add Premium", callback_data="adm_add_premium"),
            InlineKeyboardButton("❌ Remove Premium", callback_data="adm_rem_premium")
        ],
        [
            InlineKeyboardButton("🚫 Ban User", callback_data="adm_ban"),
            InlineKeyboardButton("✅ Unban User", callback_data="adm_unban")
        ],
        [
            InlineKeyboardButton("👥 All Users", callback_data="adm_users"),
            InlineKeyboardButton("💎 Premium List", callback_data="adm_premium_list")
        ],
        [
            InlineKeyboardButton("📢 Broadcast", callback_data="adm_broadcast"),
            InlineKeyboardButton("📊 Bot Stats", callback_data="adm_stats")
        ],
        [InlineKeyboardButton("🗑 Set Dump Chat", callback_data="adm_set_dump")],
        [InlineKeyboardButton("❌ Close", callback_data="adm_close")]
    ])

    if isinstance(message_or_query, Message):
        await message_or_query.reply_text(
            text, reply_markup=buttons, parse_mode=enums.ParseMode.HTML
        )
    elif isinstance(message_or_query, CallbackQuery):
        await message_or_query.edit_message_text(
            text, reply_markup=buttons, parse_mode=enums.ParseMode.HTML
        )


# ======================================================
# Admin Panel Callbacks
# ======================================================

@Client.on_callback_query(filters.regex(r"^adm_") & filters.user(ADMINS))
async def admin_callbacks(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id

    back_btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back to Admin Panel", callback_data="adm_back")]
    ])

    # --- Back to admin panel ---
    if data == "adm_back":
        ADMIN_STATE.pop(user_id, None)
        await show_admin_panel(client, callback_query)

    # --- Close ---
    elif data == "adm_close":
        ADMIN_STATE.pop(user_id, None)
        await callback_query.message.delete()

    # --- Add Premium ---
    elif data == "adm_add_premium":
        ADMIN_STATE[user_id] = {"action": "add_premium", "step": "user_id"}
        await callback_query.edit_message_text(
            "<b>👑 Add Premium</b>\n\n"
            "<i>Send the User ID to grant premium:</i>",
            reply_markup=back_btn,
            parse_mode=enums.ParseMode.HTML
        )

    # --- Premium duration selection ---
    elif data.startswith("adm_prem_days_"):
        state = ADMIN_STATE.get(user_id)
        if not state or state.get("action") != "add_premium":
            return await callback_query.answer("Session expired. Use /admin again.")

        days = int(data.split("_")[-1])
        target_uid = state["target_user_id"]

        if days == 0:
            expiry_date = None
            duration_text = "Permanent"
        else:
            expiry_date = (date.today() + timedelta(days=days)).isoformat()
            duration_text = f"{days} days (until {expiry_date})"

        await db.add_premium(target_uid, expiry_date)
        ADMIN_STATE.pop(user_id, None)

        await callback_query.edit_message_text(
            f"<b>✅ Premium Added Successfully</b>\n\n"
            f"<b>User ID:</b> <code>{target_uid}</code>\n"
            f"<b>Duration:</b> {duration_text}",
            reply_markup=back_btn,
            parse_mode=enums.ParseMode.HTML
        )

    # --- Remove Premium ---
    elif data == "adm_rem_premium":
        ADMIN_STATE[user_id] = {"action": "remove_premium", "step": "user_id"}
        await callback_query.edit_message_text(
            "<b>❌ Remove Premium</b>\n\n"
            "<i>Send the User ID to remove premium from:</i>",
            reply_markup=back_btn,
            parse_mode=enums.ParseMode.HTML
        )

    # --- Ban User ---
    elif data == "adm_ban":
        ADMIN_STATE[user_id] = {"action": "ban", "step": "user_id"}
        await callback_query.edit_message_text(
            "<b>🚫 Ban User</b>\n\n"
            "<i>Send the User ID to ban:</i>",
            reply_markup=back_btn,
            parse_mode=enums.ParseMode.HTML
        )

    # --- Unban User ---
    elif data == "adm_unban":
        ADMIN_STATE[user_id] = {"action": "unban", "step": "user_id"}
        await callback_query.edit_message_text(
            "<b>✅ Unban User</b>\n\n"
            "<i>Send the User ID to unban:</i>",
            reply_markup=back_btn,
            parse_mode=enums.ParseMode.HTML
        )

    # --- Set Dump Chat ---
    elif data == "adm_set_dump":
        ADMIN_STATE[user_id] = {"action": "set_dump", "step": "user_id"}
        await callback_query.edit_message_text(
            "<b>🗑 Set Dump Chat</b>\n\n"
            "<i>Send the User ID to set dump for:</i>",
            reply_markup=back_btn,
            parse_mode=enums.ParseMode.HTML
        )

    # --- All Users ---
    elif data == "adm_users":
        total = await db.total_users_count()
        users_cursor = await db.get_all_users()
        user_lines = []
        count = 0
        async for u in users_cursor:
            if count >= 30:
                user_lines.append(f"\n<i>...and {total - 30} more</i>")
                break
            uid = u.get("id", "?")
            name = u.get("name", "Unknown")
            is_prem = u.get("is_premium", False)
            badge = " 💎" if is_prem else ""
            is_ban = u.get("is_banned", False)
            ban_tag = " 🚫" if is_ban else ""
            user_lines.append(f"• <code>{uid}</code> — {name}{badge}{ban_tag}")
            count += 1

        user_list_text = "\n".join(user_lines) if user_lines else "<i>No users found.</i>"
        text = (
            f"<b>👥 All Users ({total})</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"{user_list_text}"
        )
        await callback_query.edit_message_text(
            text, reply_markup=back_btn, parse_mode=enums.ParseMode.HTML
        )

    # --- Premium Users List ---
    elif data == "adm_premium_list":
        premium_cursor = await db.get_premium_users()
        lines = []
        count = 0
        async for u in premium_cursor:
            uid = u.get("id", "?")
            name = u.get("name", "Unknown")
            expiry = u.get("premium_expiry")
            exp_text = str(expiry) if expiry else "Permanent"
            lines.append(f"• <code>{uid}</code> — {name} (Exp: {exp_text})")
            count += 1

        if not lines:
            list_text = "<i>No premium users found.</i>"
        else:
            list_text = "\n".join(lines)

        text = (
            f"<b>💎 Premium Users ({count})</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"{list_text}"
        )
        await callback_query.edit_message_text(
            text, reply_markup=back_btn, parse_mode=enums.ParseMode.HTML
        )

    # --- Broadcast ---
    elif data == "adm_broadcast":
        ADMIN_STATE[user_id] = {"action": "broadcast", "step": "message"}
        await callback_query.edit_message_text(
            "<b>📢 Broadcast Message</b>\n\n"
            "<i>Send the message you want to broadcast to all users.\n"
            "You can send text, photo, video, or document.</i>",
            reply_markup=back_btn,
            parse_mode=enums.ParseMode.HTML
        )

    # --- Bot Stats ---
    elif data == "adm_stats":
        total_users = await db.total_users_count()

        premium_cursor = await db.get_premium_users()
        premium_count = 0
        async for _ in premium_cursor:
            premium_count += 1

        banned_count = await db.col.count_documents({"is_banned": True})
        logged_in_count = await db.col.count_documents({"session": {"$ne": None}})

        text = (
            "<b>📊 Bot Statistics</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>👥 Total Users:</b> <code>{total_users}</code>\n"
            f"<b>💎 Premium Users:</b> <code>{premium_count}</code>\n"
            f"<b>🚫 Banned Users:</b> <code>{banned_count}</code>\n"
            f"<b>🔑 Logged In Users:</b> <code>{logged_in_count}</code>\n"
        )
        await callback_query.edit_message_text(
            text, reply_markup=back_btn, parse_mode=enums.ParseMode.HTML
        )

    await callback_query.answer()


# ======================================================
# Admin State Processing (called from start.py save handler)
# ======================================================

async def process_admin_state(client: Client, message: Message):
    """Process admin state input. Returns True if handled, False otherwise."""
    user_id = message.from_user.id
    state = ADMIN_STATE.get(user_id)

    if not state:
        return False

    action = state.get("action")
    step = state.get("step")

    back_btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back to Admin Panel", callback_data="adm_back")]
    ])

    # --- Add Premium: Step 1 - Get User ID ---
    if action == "add_premium" and step == "user_id":
        try:
            target_uid = int(message.text.strip())
        except ValueError:
            return await message.reply_text(
                "❌ <b>Invalid User ID.</b> Please send a valid number.",
                parse_mode=enums.ParseMode.HTML
            )

        ADMIN_STATE[user_id] = {
            "action": "add_premium",
            "step": "days",
            "target_user_id": target_uid
        }

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("7 Days", callback_data="adm_prem_days_7"),
                InlineKeyboardButton("30 Days", callback_data="adm_prem_days_30")
            ],
            [
                InlineKeyboardButton("90 Days", callback_data="adm_prem_days_90"),
                InlineKeyboardButton("365 Days", callback_data="adm_prem_days_365")
            ],
            [InlineKeyboardButton("♾ Permanent", callback_data="adm_prem_days_0")],
            [InlineKeyboardButton("⬅️ Back to Admin Panel", callback_data="adm_back")]
        ])

        await message.reply_text(
            f"<b>👑 Add Premium for User <code>{target_uid}</code></b>\n\n"
            "<i>Select the duration:</i>",
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )

    # --- Remove Premium: Get User ID ---
    elif action == "remove_premium" and step == "user_id":
        try:
            target_uid = int(message.text.strip())
        except ValueError:
            return await message.reply_text(
                "❌ <b>Invalid User ID.</b>",
                parse_mode=enums.ParseMode.HTML
            )

        await db.remove_premium(target_uid)
        ADMIN_STATE.pop(user_id, None)

        await message.reply_text(
            f"<b>✅ Premium Removed</b>\n\n"
            f"<b>User ID:</b> <code>{target_uid}</code>",
            reply_markup=back_btn,
            parse_mode=enums.ParseMode.HTML
        )

    # --- Ban User: Get User ID ---
    elif action == "ban" and step == "user_id":
        try:
            target_uid = int(message.text.strip())
        except ValueError:
            return await message.reply_text(
                "❌ <b>Invalid User ID.</b>",
                parse_mode=enums.ParseMode.HTML
            )

        await db.ban_user(target_uid)
        ADMIN_STATE.pop(user_id, None)

        await message.reply_text(
            f"<b>🚫 User Banned</b>\n\n"
            f"<b>User ID:</b> <code>{target_uid}</code>",
            reply_markup=back_btn,
            parse_mode=enums.ParseMode.HTML
        )

    # --- Unban User: Get User ID ---
    elif action == "unban" and step == "user_id":
        try:
            target_uid = int(message.text.strip())
        except ValueError:
            return await message.reply_text(
                "❌ <b>Invalid User ID.</b>",
                parse_mode=enums.ParseMode.HTML
            )

        await db.unban_user(target_uid)
        ADMIN_STATE.pop(user_id, None)

        await message.reply_text(
            f"<b>✅ User Unbanned</b>\n\n"
            f"<b>User ID:</b> <code>{target_uid}</code>",
            reply_markup=back_btn,
            parse_mode=enums.ParseMode.HTML
        )

    # --- Set Dump: Step 1 - Get User ID ---
    elif action == "set_dump" and step == "user_id":
        try:
            target_uid = int(message.text.strip())
        except ValueError:
            return await message.reply_text(
                "❌ <b>Invalid User ID.</b>",
                parse_mode=enums.ParseMode.HTML
            )

        ADMIN_STATE[user_id] = {
            "action": "set_dump",
            "step": "chat_id",
            "target_user_id": target_uid
        }

        await message.reply_text(
            f"<b>🗑 Set Dump for User <code>{target_uid}</code></b>\n\n"
            "<i>Now send the Chat ID for the dump channel:</i>",
            reply_markup=back_btn,
            parse_mode=enums.ParseMode.HTML
        )

    # --- Set Dump: Step 2 - Get Chat ID ---
    elif action == "set_dump" and step == "chat_id":
        try:
            chat_id = int(message.text.strip())
        except ValueError:
            return await message.reply_text(
                "❌ <b>Invalid Chat ID.</b>",
                parse_mode=enums.ParseMode.HTML
            )

        target_uid = state["target_user_id"]
        await db.set_dump_chat(target_uid, chat_id)
        ADMIN_STATE.pop(user_id, None)

        await message.reply_text(
            f"<b>✅ Dump Chat Set</b>\n\n"
            f"<b>User ID:</b> <code>{target_uid}</code>\n"
            f"<b>Chat ID:</b> <code>{chat_id}</code>",
            reply_markup=back_btn,
            parse_mode=enums.ParseMode.HTML
        )

    # --- Broadcast: Get Message ---
    elif action == "broadcast" and step == "message":
        ADMIN_STATE.pop(user_id, None)

        users = await db.get_all_users()
        total_users = await db.total_users_count()
        sts = await message.reply_text(
            "<b>📢 Broadcasting...</b>",
            parse_mode=enums.ParseMode.HTML
        )

        success = 0
        failed = 0
        done = 0

        async for user in users:
            uid = user.get("id")
            if uid:
                try:
                    await message.copy(chat_id=int(uid))
                    success += 1
                except Exception:
                    failed += 1
                done += 1

                if done % 20 == 0:
                    try:
                        await sts.edit_text(
                            f"<b>📢 Broadcasting...</b>\n\n"
                            f"<b>Done:</b> {done}/{total_users}\n"
                            f"<b>✅ Success:</b> {success}\n"
                            f"<b>❌ Failed:</b> {failed}",
                            parse_mode=enums.ParseMode.HTML
                        )
                    except Exception:
                        pass

        await sts.edit_text(
            f"<b>📢 Broadcast Completed</b>\n\n"
            f"<b>👥 Total:</b> {total_users}\n"
            f"<b>✅ Success:</b> {success}\n"
            f"<b>❌ Failed:</b> {failed}",
            reply_markup=back_btn,
            parse_mode=enums.ParseMode.HTML
        )

    else:
        return False

    return True


# Keep legacy commands working alongside the panel

@Client.on_message(filters.command("ban") & filters.user(ADMINS))
async def ban_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("**Usage:** `/ban user_id`")
    try:
        uid = int(message.command[1])
        await db.ban_user(uid)
        await message.reply_text(f"**User {uid} Banned Successfully 🚫**")
    except Exception:
        await message.reply_text("Error banning user.")

@Client.on_message(filters.command("unban") & filters.user(ADMINS))
async def unban_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("**Usage:** `/unban user_id`")
    try:
        uid = int(message.command[1])
        await db.unban_user(uid)
        await message.reply_text(f"**User {uid} Unbanned Successfully ✅**")
    except Exception:
        await message.reply_text("Error unbanning user.")

@Client.on_message(filters.command("set_dump") & filters.user(ADMINS))
async def set_dump_cmd(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("**Usage:** `/set_dump user_id chat_id`")
    try:
        uid = int(message.command[1])
        chat_id = int(message.command[2])
        await db.set_dump_chat(uid, chat_id)
        await message.reply_text(f"**Dump chat set for user {uid}.**")
    except Exception:
        await message.reply_text("Error setting dump chat.")

@Client.on_message(filters.command("dblink") & filters.user(ADMINS))
async def dblink_cmd(client: Client, message: Message):
    await message.reply_text(f"**DB URI:** `{DB_URI}`")

# cantarella
# Don't Remove Credit
# Telegram Channel @cantarellabots
