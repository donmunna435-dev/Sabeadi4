# 📥 Restricted Content Download Bot

A professional Telegram bot for downloading restricted content from private channels, groups, and bots.

**Made by:** Surya (@tataa_sumo)  
**Channel:** @idfinderpro

---

## ✨ Features

### 🔐 **Authentication System**
- Secure login with Telegram account
- Session-based authentication
- Auto-join private channels via invite links

### 💎 **Premium Membership**
- **Free Plan:** 10 successful downloads/day
- **Premium Plan:** Unlimited downloads (no daily limit)
- Redeem code system
- Contact admin for premium access

### 📥 **Download Capabilities**
- Download from private channels
- Download from public channels
- Download from bots
- Batch download support (ranges)
- Auto file cleanup to save storage

### 🔒 **Force Subscription**
- Users must join @idfinderpro channel
- Automatic membership verification
- Join button for easy subscription

### 👨‍💻 **Admin Panel**
- Generate redeem codes (1/7/30 days)
- Manage premium users
- View statistics
- Broadcast messages

---

## 🚀 Quick Start

### For Users:
1. Start the bot: `/start`
2. Join channel: @idfinderpro (required)
3. Login: `/login`
4. Send any Telegram post link
5. Download restricted content!

### For Premium:
- Check pricing: `/premium`
- Contact admin: @tataa_sumo
- Redeem code: `/redeem <code>`

---

## 📋 Commands

### **User Commands:**
- `/start` - Start the bot
- `/help` - Interactive help guide
- `/login` - Login with Telegram
- `/logout` - Logout account
- `/premium` - Premium membership info
- `/redeem <code>` - Activate premium
- `/cancel` - Cancel batch download

### **Admin Commands:**
- `/admin` - Admin panel
- `/generate` - Generate redeem codes
- `/premiumlist` - Manage premium users
- `/processes` - View active downloads
- `/exportdata` - Export user database (CSV)

---

## 💰 Premium Pricing

| Duration | INR Price | USDT (approx) |
|----------|-----------|---------------|
| 1 Day | ₹20 | ~0.24 USDT |
| 7 Days | ₹50 | ~0.60 USDT |
| 30 Days | ₹100 | ~1.20 USDT |

**Payment Methods:**
- UPI
- Bank Transfer
- Cryptocurrency

**Contact:** @tataa_sumo for payment details

---

## 📥 How to Download

### **Public Channels:**
```
https://t.me/channelname/123
```

### **Private Channels:**
1. Send invite link: `https://t.me/+InviteHash`
2. Send post link: `https://t.me/c/123456789/100`

### **Batch Download:**
```
https://t.me/channel/100-110
```

### **From Bots:**
```
https://t.me/b/botusername/4321
```

---

## ⚙️ Configuration

### Environment Variables:

```env
BOT_TOKEN=your_bot_token
API_ID=your_api_id
API_HASH=your_api_hash
ADMINS=your_admin_user_id
DB_URI=your_mongodb_uri
DB_NAME=idfinderpro
CHANNEL_ID=-1002441460670
```

### config.py:
- `FORCE_SUB_CHANNEL` - Channel username for force subscription
- `FORCE_SUB_CHANNEL_ID` - Channel ID
- `LOG_CHANNEL_ID` - Channel ID for logging downloads (set to 0 to disable)
- `ADMINS` - Admin user ID

---

## 🗄️ Database Structure

```python
{
    "id": user_id,
    "name": user_name,
    "session": session_string,
    "is_premium": False,
    "premium_expiry": timestamp,
    "downloads_today": 0,
    "last_download_date": "2025-10-09"
}
```

**Database:** MongoDB  
**Collections:** users

---

## 📦 Installation

### 1. Clone Repository:
```bash
git clone https://github.com/suryapaul01/save-restricted-bot.git
cd save-restricted-bot
```

### 2. Install Dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configure:
Edit `config.py` with your credentials

### 4. Run:
```bash
python bot.py
```

---

## 📂 Project Structure

```
.
├── bot.py                 # Main bot file
├── config.py             # Configuration
├── database/
│   └── db.py            # Database operations
├── IdFinderPro/
│   ├── start.py         # Main handlers & download logic
│   ├── generate.py      # Login/Logout
│   ├── premium.py       # Premium system
│   ├── broadcast.py     # Broadcast feature
│   └── strings.py       # Help texts
├── requirements.txt      # Dependencies
└── README.md            # This file
```

---

## 🔧 Technical Details

### Built With:
- **Pyrogram/Pyrofork** - MTProto API
- **MongoDB** - Database
- **Flask** - Web server (for deployment)
- **Python 3.13**

### Features:
- Async/await architecture
- Session-based authentication
- Rate limiting system
- Premium membership management
- Force subscription
- Auto file cleanup
- Batch download support
- Log channel for monitoring downloads
- Process tracking for active downloads

---

## 🚀 Deployment

### Heroku/Koyeb:
- Set environment variables
- Deploy using `Procfile`
- Ensure MongoDB is accessible

### VPS:
```bash
python bot.py
```

For production, use process managers like PM2 or systemd.

---

## 📊 Rate Limits

| Plan | Downloads/Day |
|------|---------------|
| Free | 10 |
| Premium | Unlimited |

**Important:**
- Only **successful downloads** are counted towards your limit
- Failed downloads do not consume your quota
- For range downloads (e.g., 100-110), the bot checks if you have enough limit before processing
- Premium users enjoy unlimited downloads with no daily restrictions

**Resets:** Daily at midnight (UTC)  
**Tracking:** Per user basis

---

## 🔒 Security

- ✅ Secure session storage
- ✅ Encrypted database
- ✅ Admin-only commands protected
- ✅ Force subscription enforcement
- ✅ Rate limiting to prevent abuse
- ✅ Auto file cleanup

---

## 💡 Tips

- Login before downloading
- Join @idfinderpro for updates
- Use `/premium` to check your limits
- Use `/help` for interactive guide
- Contact @tataa_sumo for premium

---

## 📢 Support

- **Channel:** @idfinderpro
- **Developer:** @tataa_sumo
- **Issues:** Open an issue on GitHub

---

## 📝 License

This project is for educational purposes.

---

## ⚠️ Troubleshooting

### SESSION_REVOKED Error

If you get `pyrogram.errors.exceptions.unauthorized_401.SessionRevoked` error:

**On VPS/Production:**
```bash
# Delete the revoked session file
rm -f idfinderpro.session
rm -f idfinderpro.session-journal

# Restart the bot - it will create a fresh session
python3 bot.py
```

**Locally:**
```bash
# Delete session files
del idfinderpro.session
del idfinderpro.session-journal  # Windows

# Or on Linux/Mac
rm -f idfinderpro.session idfinderpro.session-journal

# Run the bot
python bot.py
```

**Note:** Session files are now in `.gitignore` for security. The bot creates them automatically.

---

## 🙏 Credits

**Developed by:** Surya  
**Telegram:** @tataa_sumo  
**Channel:** @idfinderpro

---

## 🆕 Recent Updates

### Version 2.1 (Latest)
- ✅ Fixed download tracking - now counts only successful downloads
- ✅ Premium users now have unlimited downloads (not 1000/day)
- ✅ Range download limit checking - validates before processing
- ✅ Improved user prompts when limits are exceeded
- ✅ Better upgrade to premium messaging
- ✅ Added `/processes` command for admins
- ✅ Added `/exportdata` command to export user database
- ✅ Log channel feature - forwards all downloads to monitoring channel
- ✅ Process tracking with elapsed time display

### Version 2.0
- ✅ Complete rebranding
- ✅ Premium membership system
- ✅ Force subscription
- ✅ Rate limiting
- ✅ Admin panel
- ✅ Redeem code system
- ✅ Professional UI/UX
- ✅ Removed channel forwarding
- ✅ Enhanced help system

---

**⭐ Star this repo if you find it useful!**

Repository: https://github.com/suryapaul01/save-restricted-bot
