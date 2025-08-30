# 🩺 HealthBot

![HealthBot](https://img.shields.io/badge/HealthBot-Python-blue?logo=python\&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Telegram](https://img.shields.io/badge/Platform-Telegram-blue)

**HealthBot** adalah bot Telegram cerdas untuk pengingat obat, summary harian, dan konsultasi kesehatan AI. Dirancang agar mudah digunakan dengan **keyboard interaktif** dan notifikasi otomatis.



## 🌟 Fitur Unggulan

| Fitur                      | Deskripsi                                                                          |
| -------------------------- | ---------------------------------------------------------------------------------- |
| 💬 Konsultasi AI           | Tanyakan masalah kesehatan dasar, dapatkan jawaban AI.                             |
| ⏰ Reminder Obat            | Tambahkan obat dengan jam minum tertentu, HealthBot akan mengingatkan tepat waktu. |
| 📋 Summary Obat Harian     | Mendapatkan daftar obat yang harus diminum setiap hari.                            |
| ➕ Tambah/Hapus Obat        | Menambahkan atau menghapus obat dari daftar reminder.                              |
| ⏰ Tambah/Hapus Jam Summary | Mengatur jam pengiriman summary sesuai kebutuhan.                                  |
| 📢 Broadcast Admin         | Admin dapat mengirim pesan ke semua pengguna bot.                                  |
| 👥 User Count Admin        | Menampilkan jumlah pengguna bot secara realtime.                                   |
| ✅ Cron Job Otomatis        | Mengirim reminder obat dan summary sesuai jadwal.                                  |


## 🛠 Teknologi yang Digunakan

* **Bahasa:** Python 3.12+
* **Bot Framework:** [python-telegram-bot](https://python-telegram-bot.org/)
* **Database:** SQLite
* **Scheduler:** APScheduler
* **HTTP Requests:** `requests`
* **Environment Variables:** `python-dotenv`


## ⚡ Cara Install

1. **Clone repository**

```bash
git clone https://github.com/Cylne/HEALTH_BOT.git
cd HealthBot
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Buat file `.env`**

```env
TELEGRAM_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
AI_API=https://api.ferdev.my.id/ai/chatgpt
AI_KEY=YOUR_AI_KEY
ADMIN_ID=YOUR_TELEGRAM_ID
```

4. **Jalankan bot**

```bash
python bot.py
```

5. **Gunakan bot di Telegram**

   * Ketik `/start` untuk memulai
   * Gunakan **keyboard interaktif** untuk navigasi menu


## 📸 Tampilan Bot (Mockup)

![Image](https://github.com/user-attachments/assets/df052b9e-9b83-4493-8a14-639d6c72598e)

**Menu Utama:**

```
💬 Konsultasi Kesehatan
➕ Tambah Obat     📋 Daftar Obat
❌ Hapus Obat
⏰ Tambah Jam Summary   🗑 Hapus Jam Summary
📢 Broadcast (Admin)   👥 Users (Admin)
```

**Pesan Reminder Obat:**

```
⏰ Saatnya minum obat: Paracetamol
```

**Summary Obat Harian:**

```
📋 Summary obat harian kamu:

1. Paracetamol ⏰ 08:00
2. Vitamin C ⏰ 12:00
```

**Broadcast Admin:**

```
📢 Broadcast dari admin:

Halo semua! Jangan lupa cek jadwal obat kalian hari ini.
```

**Konsultasi AI:**

```
💬 Ketik pertanyaan kesehatanmu:
> Saya demam, apa yang harus saya lakukan?
🤖 Hello! Jangan lupa istirahat cukup dan minum air putih. Jika gejala berlanjut, konsultasikan ke dokter.
```

> 💡 Mockup ini bisa diganti dengan screenshot asli Telegram saat bot dijalankan.


## 🔧 Catatan Penting

* Pastikan koneksi internet stabil.
* Gunakan **AI API key** yang valid agar fitur konsultasi kesehatan berjalan.
* **Admin ID** diperlukan untuk broadcast dan user count.
* SQLite digunakan agar bot mudah dijalankan tanpa setup server tambahan.


## 📜 Lisensi

MIT License © 2025 Cylne Project

Telegram : @Hiicylne

Channel Telegram : https://t.me/Cylneee
