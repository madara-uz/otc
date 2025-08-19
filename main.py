from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import GetParticipant
from telethon.tl.types import ChannelParticipantSelf
import sqlite3
from config import API_ID, API_HASH, BOT_TOKEN, REQUIRED_CHANNELS

# =========================
# Database tayyorlash
# =========================
conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    profile_created INTEGER DEFAULT 0,
    top INTEGER DEFAULT 0,
    sent REAL DEFAULT 0,
    received REAL DEFAULT 0,
    speed TEXT DEFAULT 'super tez'
)
""")
conn.commit()

# =========================
# Bot client
# =========================
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# =========================
# Kanalga obuna tekshirish funksiyasi
# =========================
async def is_subscribed(client, user_id, channel_username):
    try:
        participant = await client(GetParticipant(channel=channel_username, participant=user_id))
        if isinstance(participant.participant, ChannelParticipantSelf):
            return True
    except:
        return False
    return False

# =========================
# /start handler
# =========================
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id
    username = event.sender.username or event.sender.first_name

    # Foydalanuvchi bazada mavjudligini tekshirish
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if user:
        # Foydalanuvchi allaqachon mavjud, lekin kanalga obuna ekanligini tekshirish
        subscribed_all = all([await is_subscribed(bot, user_id, ch) for ch in REQUIRED_CHANNELS])
        if subscribed_all:
            profile_text = f"""
Profil ID: {user[0]}
Username: {user[1]}
Top: {user[3]}
Yuborgan: {user[4]}
Qabul qilgan: {user[5]}
Sifat: {user[6]}
"""
            buttons = [
                [Button.inline("Bitim ochish", b"new_deal"),
                 Button.inline("Hamyon", b"wallet")],
                [Button.inline("Support", b"support"),
                 Button.inline("Tranzaksiyalar tarixi", b"history")]
            ]
            await event.respond("Sizning profilingiz:", buttons=buttons)
            return

    # Agar foydalanuvchi yangi bo‘lsa yoki kanalga obuna bo‘lmagan bo‘lsa
    buttons = [
        [Button.url(f"{ch}", f"https://t.me/{ch}")] for ch in REQUIRED_CHANNELS
    ]
    buttons.append([Button.inline("Obuna bo'ldim", b"subscribed")])
    await event.respond(
        "Salom! Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:",
        buttons=buttons
    )

# =========================
# Obuna tugmasi handler
# =========================
@bot.on(events.CallbackQuery(data=b"subscribed"))
async def subscribed(event):
    user_id = event.sender_id
    username = event.sender.username or event.sender.first_name

    # Foydalanuvchi kanalga obuna ekanligini tekshirish
    subscribed_all = all([await is_subscribed(bot, user_id, ch) for ch in REQUIRED_CHANNELS])
    if not subscribed_all:
        await event.answer("Iltimos, barcha kanallarga obuna bo‘ling!", alert=True)
        return

    # Foydalanuvchi bazada mavjudligini tekshirish
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        # Yangi profil yaratish
        cursor.execute(
            "INSERT INTO users (user_id, username, profile_created) VALUES (?, ?, ?)",
            (user_id, username, 1)
        )
        conn.commit()
        await event.edit("Profil yaratildi ✅")
    else:
        await event.edit("Profilingiz allaqachon mavjud ✅")

    # Profil ma'lumotlarini ko‘rsatish
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user_data = cursor.fetchone()
    profile_text = f"""
Profil ID: {user_data[0]}
Username: {user_data[1]}
Top: {user_data[3]}
Yuborgan: {user_data[4]}
Qabul qilgan: {user_data[5]}
Sifat: {user_data[6]}
"""
    buttons = [
        [Button.inline("Bitim ochish", b"new_deal"),
         Button.inline("Hamyon", b"wallet")],
        [Button.inline("Support", b"support"),
         Button.inline("Tranzaksiyalar tarixi", b"history")]
    ]
    await event.respond(profile_text, buttons=buttons)

# =========================
# Bot ishga tushishi
# =========================
print("Bot ishga tushdi...")
bot.run_until_disconnected()
    
