# Save Restricted Content Bot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&style=for-the-badge">
  <img src="https://img.shields.io/badge/Library-Pyrogram-yellow?logo=telegram&style=for-the-badge">
  <img src="https://img.shields.io/badge/Database-MongoDB-green?logo=mongodb&style=for-the-badge">
  <img src="https://img.shields.io/badge/Status-Stable-success?style=for-the-badge">
</p>

<p align="center">
<b>Save Restricted Content Bot - owned and operated by @Anonononononon</b>
</p>

---

# 🚀 Features

<details open>
<summary><b>📦 Core Features</b></summary>

- **Save Restricted Content** — Download text, media, and files from restricted channels.
- **Batch Mode** — Bulk download messages from public or private channels with auto-detection.
- **User Login** — Login using `/login` to enable downloading capabilities.

### ⚙️ Customization

- Set custom captions (`/set_caption`)
- Set custom thumbnails (`/set_thumb`)
- Auto-delete or replace specific words

### 💎 Premium System

- Built-in system for free and premium users
- Admin-controlled premium access

### 👑 Admin Tools

- Broadcast messages
- Ban / Unban users
- Manage premium status

### 🧠 Persistent Storage

- MongoDB-based user data and settings

### ☁️ Keep Alive

- Supports uptime services for Render / Heroku deployments

</details>

---

# 🛠 Deployment

## ✅ Prerequisites

- Python **3.10+**
- MongoDB Database
- Telegram API ID & Hash
- Bot Token

---

## ⚙️ Environment Variables

<details>
<summary><b>Click to Expand</b></summary>

| Variable        | Description                                |
| --------------- | ------------------------------------------ |
| `BOT_TOKEN`     | Telegram Bot Token from BotFather          |
| `API_ID`        | Telegram API ID                            |
| `API_HASH`      | Telegram API Hash                          |
| `ADMINS`        | Comma-separated Admin User IDs             |
| `DB_URI`        | MongoDB Connection String                  |
| `DB_NAME`       | Database Name (default: `SaveRestricted2`) |
| `LOG_CHANNEL`   | Channel ID for logging users and errors    |
| `ERROR_MESSAGE` | Send error messages to users               |
| `KEEP_ALIVE`    | Use an uptime service like UptimeRobot     |

</details>

---

## 💻 Local Setup

<details open>
<summary><b>Installation Steps</b></summary>

### Clone the repository

```bash
git clone https://github.com/Aman262626/SAVE-RESTRICT-BOT-AMAX.git
cd SAVE-RESTRICT-BOT-AMAX
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the bot

```bash
python bot.py
```

</details>

---

## 🐳 Docker

```bash
docker build -t save-restricted-bot .
docker run -d --env-file .env save-restricted-bot
```

---

# 📝 Commands

## 👤 User Commands

<details>
<summary><b>Click to Expand</b></summary>

| Command     | Action                   |
| ----------- | ------------------------ |
| `/start`    | Start the bot            |
| `/help`     | Get help information     |
| `/login`    | Login to your account    |
| `/logout`   | Logout from your account |
| `/cancel`   | Cancel batch process     |
| `/settings` | Open settings menu       |
| `/myplan`   | Check your current plan  |
| `/premium`  | View premium details     |

### ⚙️ Customization

- `/set_caption`
- `/see_caption`
- `/del_caption`
- `/set_thumb`
- `/view_thumb`
- `/del_thumb`
- `/thumb_mode`
- `/set_del_word`
- `/rem_del_word`
- `/set_repl_word`
- `/rem_repl_word`
- `/setchat`

</details>

---

## 👑 Admin Commands

<details>
<summary><b>Click to Expand</b></summary>

- `/broadcast`
- `/ban` / `/unban`
- `/add_premium` / `/remove_premium`
- `/users`
- `/premium_users`
- `/set_dump`
- `/dblink`

</details>

---

# 📞 Support

<p align="center">
  <a href="https://t.me/Anonononononon">
    <img src="https://img.shields.io/badge/Owner-@Anonononononon-blue?style=for-the-badge&logo=telegram">
  </a>
</p>
