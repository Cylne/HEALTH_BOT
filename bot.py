import sqlite3
import os
import re
import requests
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# ====================== ENV ======================
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
AI_API = os.getenv("AI_API")
AI_KEY = os.getenv("AI_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# ====================== DATABASE ======================
conn = sqlite3.connect("healthbot.db", check_same_thread=False)
c = conn.cursor()

# reminders
c.execute("""CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userId INTEGER,
    medicine TEXT,
    time TEXT
)""")

# usersettings (summaryTimes disimpan sebagai CSV)
c.execute("""CREATE TABLE IF NOT EXISTS usersettings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userId INTEGER,
    summaryTimes TEXT
)""")
conn.commit()

# ====================== STATE ======================
waiting_for_medicine = {}        # chat_id: {"step":"nama"/"jam","medicine":""}
waiting_for_consult = {}
waiting_for_delete = {}
waiting_for_add_summary = {}
waiting_for_delete_summary = {}
waiting_for_broadcast = {}

# ====================== BOT ======================
app = ApplicationBuilder().token(TOKEN).build()

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    keyboard = [
        ["💬 Konsultasi Kesehatan"],
        ["➕ Tambah Obat", "📋 Daftar Obat"],
        ["❌ Hapus Obat"],
        ["⏰ Tambah Jam Summary", "🗑 Hapus Jam Summary"]
    ]
    if chat_id == ADMIN_ID:
        keyboard.append(["📢 Broadcast", "👥 Users"])
    await update.message.reply_text(
        "👋 Selamat datang di HealthBot!\n\n"
        "- 💬 Konsultasi AI\n"
        "- ⏰ Reminder obat\n"
        "- 📋 Summary obat harian",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

app.add_handler(CommandHandler("start", start))

# ===== KONSULTASI AI =====
async def consult_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    waiting_for_consult[chat_id] = True
    await update.message.reply_text("Ketik pertanyaan kesehatanmu:")

app.add_handler(MessageHandler(filters.Regex("💬 Konsultasi Kesehatan"), consult_handler))

# ===== TAMBAH OBAT =====
async def add_medicine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    waiting_for_medicine[chat_id] = {"step": "nama", "medicine": ""}
    await update.message.reply_text("Masukkan nama obat:")

app.add_handler(MessageHandler(filters.Regex("➕ Tambah Obat"), add_medicine))

# ===== DAFTAR OBAT =====
async def list_medicine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    c.execute("SELECT medicine, time FROM reminders WHERE userId=?", (chat_id,))
    reminders = c.fetchall()
    if not reminders:
        return await update.message.reply_text("📭 Kamu belum punya reminder obat.")
    text = "📋 Daftar obat:\n"
    for i, (med, time) in enumerate(reminders, 1):
        text += f"{i}. {med} ⏰ {time}\n"
    await update.message.reply_text(text)

app.add_handler(MessageHandler(filters.Regex("📋 Daftar Obat"), list_medicine))

# ===== HAPUS OBAT =====
async def delete_medicine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    c.execute("SELECT id, medicine, time FROM reminders WHERE userId=?", (chat_id,))
    reminders = c.fetchall()
    if not reminders:
        return await update.message.reply_text("⚠️ Tidak ada obat untuk dihapus.")
    text = "\n".join([f"{i+1}. {med} ⏰ {time}" for i,(id,med,time) in enumerate(reminders)])
    await update.message.reply_text(f"Pilih nomor obat yang mau dihapus:\n{text}")
    waiting_for_delete[chat_id] = reminders

app.add_handler(MessageHandler(filters.Regex("❌ Hapus Obat"), delete_medicine))

# ===== TAMBAH JAM SUMMARY =====
async def add_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    waiting_for_add_summary[chat_id] = True
    await update.message.reply_text("Masukkan jam summary baru (HH:mm, contoh 06:30)")

app.add_handler(MessageHandler(filters.Regex("⏰ Tambah Jam Summary"), add_summary))

# ===== HAPUS JAM SUMMARY =====
async def delete_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    c.execute("SELECT summaryTimes FROM usersettings WHERE userId=?", (chat_id,))
    data = c.fetchone()
    if not data or not data[0]:
        return await update.message.reply_text("⚠️ Kamu belum punya jam summary.")
    times = data[0].split(",")
    text = "\n".join([f"{i+1}. {t}" for i,t in enumerate(times)])
    await update.message.reply_text(f"Pilih nomor jam summary yang mau dihapus:\n{text}")
    waiting_for_delete_summary[chat_id] = times

app.add_handler(MessageHandler(filters.Regex("🗑 Hapus Jam Summary"), delete_summary))

# ===== BROADCAST ADMIN =====
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    if chat_id != ADMIN_ID:
        return await update.message.reply_text("⚠️ Hanya admin yang bisa broadcast.")
    waiting_for_broadcast[chat_id] = True
    await update.message.reply_text("Ketik pesan broadcast:")

app.add_handler(MessageHandler(filters.Regex("📢 Broadcast"), broadcast))

# ===== USER COUNT ADMIN =====
async def user_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    if chat_id != ADMIN_ID:
        return await update.message.reply_text("⚠️ Hanya admin yang bisa melihat jumlah pengguna.")
    c.execute("SELECT COUNT(DISTINCT userId) FROM reminders")
    count = c.fetchone()[0]
    await update.message.reply_text(f"👥 Jumlah pengguna bot: {count}")

app.add_handler(MessageHandler(filters.Regex("👥 Users"), user_count))

# ===== STATE HANDLER TEKS =====
async def state_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    text = update.message.text

    # -- KONSULTASI AI --
    if chat_id in waiting_for_consult:
        try:
            res = requests.get(f"{AI_API}?prompt={text}&apikey={AI_KEY}").json()
            await update.message.reply_text(f"🤖 {res['message']}")
        except:
            await update.message.reply_text("⚠️ Gagal terhubung ke AI.")
        del waiting_for_consult[chat_id]
        return

    # -- TAMBAH OBAT --
    if chat_id in waiting_for_medicine:
        data = waiting_for_medicine[chat_id]
        if data["step"] == "nama":
            waiting_for_medicine[chat_id] = {"step": "jam", "medicine": text}
            await update.message.reply_text("Masukkan jam minum obat (HH:mm):")
            return
        elif data["step"] == "jam":
            if not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", text):
                return await update.message.reply_text("⚠️ Format salah. Gunakan HH:mm")
            c.execute("INSERT INTO reminders (userId, medicine, time) VALUES (?,?,?)",
                      (chat_id, data["medicine"], text))
            conn.commit()
            await update.message.reply_text(f"✅ Obat *{data['medicine']}* diingatkan pada jam *{text}*", parse_mode="Markdown")
            del waiting_for_medicine[chat_id]
            return

    # -- HAPUS OBAT --
    if chat_id in waiting_for_delete:
        try:
            idx = int(text)-1
            rem = waiting_for_delete[chat_id][idx]
            c.execute("DELETE FROM reminders WHERE id=?", (rem[0],))
            conn.commit()
            await update.message.reply_text(f"✅ Obat *{rem[1]}* berhasil dihapus.", parse_mode="Markdown")
        except:
            await update.message.reply_text("⚠️ Nomor tidak valid.")
        del waiting_for_delete[chat_id]
        return

    # -- TAMBAH SUMMARY --
    if chat_id in waiting_for_add_summary:
        if not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", text):
            return await update.message.reply_text("⚠️ Format salah. Gunakan HH:mm")
        c.execute("SELECT summaryTimes FROM usersettings WHERE userId=?", (chat_id,))
        data_db = c.fetchone()
        if not data_db:
            c.execute("INSERT INTO usersettings (userId, summaryTimes) VALUES (?,?)", (chat_id, text))
        else:
            times = data_db[0].split(",")
            if text not in times:
                times.append(text)
                c.execute("UPDATE usersettings SET summaryTimes=? WHERE userId=?", (",".join(times), chat_id))
        conn.commit()
        await update.message.reply_text(f"✅ Jam summary baru ditambahkan: *{text}*", parse_mode="Markdown")
        del waiting_for_add_summary[chat_id]
        return

    # -- HAPUS SUMMARY --
    if chat_id in waiting_for_delete_summary:
        try:
            idx = int(text)-1
            times = waiting_for_delete_summary[chat_id]
            removed = times.pop(idx)
            c.execute("UPDATE usersettings SET summaryTimes=? WHERE userId=?", (",".join(times), chat_id))
            conn.commit()
            await update.message.reply_text(f"✅ Jam summary *{removed}* berhasil dihapus.", parse_mode="Markdown")
        except:
            await update.message.reply_text("⚠️ Nomor tidak valid.")
        del waiting_for_delete_summary[chat_id]
        return

    # -- BROADCAST --
    if chat_id in waiting_for_broadcast:
        try:
            c.execute("SELECT DISTINCT userId FROM reminders")
            users = c.fetchall()
            for (uid,) in users:
                app.bot.send_message(uid, f"📢 Broadcast dari admin:\n\n{text}")
            await update.message.reply_text(f"✅ Broadcast terkirim ke {len(users)} pengguna.")
        except:
            await update.message.reply_text("⚠️ Gagal mengirim broadcast.")
        del waiting_for_broadcast[chat_id]
        return

app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), state_handler))

# ===== CRON REMINDER OBAT =====
def cron_reminder():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    c.execute("SELECT userId, medicine FROM reminders WHERE time=?", (current_time,))
    rows = c.fetchall()
    for uid, med in rows:
        app.bot.send_message(uid, f"⏰ Saatnya minum obat: *{med}*", parse_mode="Markdown")

scheduler = BackgroundScheduler()
scheduler.add_job(cron_reminder, 'cron', minute='*')
scheduler.start()

# ===== START BOT =====
print("🤖 HealthBot running...")
app.run_polling()