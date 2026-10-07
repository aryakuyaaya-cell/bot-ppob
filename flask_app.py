import os
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from google import genai

# --- KREDENSIAL (ISI DENGAN DATA ASLI) ---
TOKEN = '8654258790:AAEz8WelOJrqxRHXU3iY6r3vhW0mwaZNcSA'
GEMINI_API_KEY = 'ISI_DENGAN_API_KEY_GEMINI_YANG_BARU' # Ambil dari Google AI Studio

# Kredensial Digiflazz Production
DIGIFLAZZ_USERNAME = "mudafooJvA3o"
DIGIFLAZZ_API_KEY = "ISI_DENGAN_API_KEY_DIGIFLAZZ_PRODUCTION" 
DIGIFLAZZ_URL = "https://api.digiflazz.com/v1/transaction"

client = genai.Client(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- FUNGSI MENU UTAMA CIAMIK ---
def menu_utama():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📱 Pulsa & Data", callback_data="kategori_pulsa"),
        InlineKeyboardButton("⚡ Token PLN", callback_data="kategori_pln"),
        InlineKeyboardButton("💸 E-Wallet", callback_data="kategori_ewallet"),
        InlineKeyboardButton("👤 Akun Saya", callback_data="menu_akun")
    )
    markup.add(InlineKeyboardButton("🤖 Bantuan AI Gemini", callback_data="menu_ai"))
    return markup

@bot.message_handler(commands=['start'])
def start_bot(message):
    teks = (
        "🚀 *Selamat datang di Bot PPOB & AI Asisten!*\n\n"
        "Silakan pilih layanan transaksi di bawah ini, atau langsung ketik pesan apa saja untuk ngobrol dengan AI."
    )
    bot.reply_to(message, teks, reply_markup=menu_utama(), parse_mode="Markdown")

# --- HANDLER KLIK TOMBOL (CALLBACK) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    data = call.data

    if data == "kembali_utama":
        bot.edit_message_text("🚀 *Silakan pilih layanan PPOB:*", chat_id, msg_id, reply_markup=menu_utama(), parse_mode="Markdown")

    elif data == "kategori_pulsa":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("Telkomsel", callback_data="opsi_tsel"),
            InlineKeyboardButton("Indosat", callback_data="opsi_isat"),
            InlineKeyboardButton("XL / Axis", callback_data="opsi_xl"),
            InlineKeyboardButton("🔙 Kembali", callback_data="kembali_utama")
        )
        bot.edit_message_text("📱 *Pilih Operator:*", chat_id, msg_id, reply_markup=markup, parse_mode="Markdown")

    elif data == "kategori_ewallet":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("Dana", callback_data="opsi_dana"),
            InlineKeyboardButton("Gopay", callback_data="opsi_gopay"),
            InlineKeyboardButton("Ovo", callback_data="opsi_ovo"),
            InlineKeyboardButton("ShopeePay", callback_data="opsi_spay"),
            InlineKeyboardButton("🔙 Kembali", callback_data="kembali_utama")
        )
        bot.edit_message_text("💸 *Pilih E-Wallet:*", chat_id, msg_id, reply_markup=markup, parse_mode="Markdown")
        
    elif data == "kategori_pln":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Kembali", callback_data="kembali_utama"))
        bot.edit_message_text("⚡ *Kategori PLN sedang disiapkan...*", chat_id, msg_id, reply_markup=markup, parse_mode="Markdown")

    elif data == "menu_akun":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Kembali", callback_data="kembali_utama"))
        bot.edit_message_text(f"👤 *Data Akun*\nID Telegram Anda: `{chat_id}`\nStatus: Terverifikasi", chat_id, msg_id, reply_markup=markup, parse_mode="Markdown")
        
    elif data == "menu_ai":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Kembali", callback_data="kembali_utama"))
        bot.edit_message_text("🤖 *Fitur AI Aktif!*\nKetik pertanyaan, buat caption promosi afiliasi, atau ngobrol santai langsung di chat ini. AI akan otomatis merespons.", chat_id, msg_id, reply_markup=markup, parse_mode="Markdown")

# --- HANDLER PESAN TEKS (AI GEMINI) ---
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        # Bikin status bot "typing..." biar kelihatan hidup
        bot.send_chat_action(message.chat.id, 'typing')
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Jawab dengan asik, ringkas, dan seperti asisten pintar: {message.text}"
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Waduh AI-nya lagi pusing. Pastikan API Key Gemini udah diisi dengan benar ya bray!")

# --- MESIN PENGGERAK SERVER & POLLING ---
def jalankan_polling():
    bot.remove_webhook()
    bot.infinity_polling()

@app.route('/')
def index():
    return "Server PPOB Ciamik Aktif!", 200

if __name__ == '__main__':
    thread = threading.Thread(target=jalankan_polling)
    thread.start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
