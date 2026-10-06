import telebot
import os
import hashlib
import requests
from google import genai
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- DATA KREDENSIAL ---
TOKEN = TOKEN = '8654258790:AAEz8WelOJrqxRHXU3iY6r3vhW0mwaZNcSA'
GEMINI_API_KEY = 'AQ.Ab8RN6IqzTlrvnBaghoVDi9bYXo9NW2VX4T9JF9wJgc7_mkggQ'

# Kredensial Digiflazz Sandbox
DIGIFLAZZ_USERNAME = "mudafooJvA3o"
DIGIFLAZZ_API_KEY = "dev-197d6900-c160-11f1-8df3-0dc49c4b125"
DIGIFLAZZ_URL = "https://api.digiflazz.com/v1/transaction"

# Inisialisasi Klien Gemini Baru
client = genai.Client(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- MENU UTAMA ---
def buat_menu_utama():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("🛍️ Layanan PPOB", callback_data="menu_ppob"),
        InlineKeyboardButton("👤 Akun Saya", callback_data="menu_akun"),
        InlineKeyboardButton("💡 Bantuan Promosi", callback_data="menu_bantuan")
    )
    return markup

@bot.message_handler(commands=['start'])
def start_bot(message):
    pesan_sapaan = "Halo! Selamat datang di **Asisten Promosi & Layanan PPOB**. 🚀\n\nKirimkan langsung link produk ke sini untuk buat caption afiliasi, atau pilih menu PPOB di bawah ini:"
    bot.reply_to(message, pesan_sapaan, reply_markup=buat_menu_utama(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data
    if data == "menu_utama":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Silakan pilih menu utama di bawah ini:", reply_markup=buat_menu_utama())
    elif data == "menu_ppob":
        markup_ppob = InlineKeyboardMarkup(row_width=2)
        markup_ppob.add(
            InlineKeyboardButton("📱 Pulsa XL 10rb (Test Sandbox)", callback_data="buy_xld10_12000_087800001232"),
            InlineKeyboardButton("🔙 Kembali", callback_data="menu_utama")
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🛠 *Kategori Layanan PPOB*\nSilakan pilih produk uji coba:", reply_markup=markup_ppob, parse_mode="Markdown")
    elif data.startswith("buy_"):
        parts = data.split("_")
        sku = parts[1]
        nomor_target = parts[3]
        
        ref_id = f"TRX_{call.from_user.id}_{int(os.urandom(2).hex(), 16)}"
        raw_sign = DIGIFLAZZ_USERNAME + DIGIFLAZZ_API_KEY + ref_id
        sign = hashlib.md5(raw_sign.encode()).hexdigest()
        
        payload = {
            "username": DIGIFLAZZ_USERNAME,
            "buyer_sku_code": sku,
            "customer_no": nomor_target,
            "ref_id": ref_id,
            "sign": sign,
            "testing": True
        }
        
        try:
            session = requests.Session()
            session.trust_env = False
            res = session.post(DIGIFLAZZ_URL, json=payload, headers={'Content-Type': 'application/json'}, timeout=15)
            
            res_json = res.json().get('data', {})
            status_transaksi = res_json.get('message', 'Diproses')
            rc_code = res_json.get('rc', '-')
            
            bot.edit_message_text(
                chat_id=call.message.chat.id, 
                message_id=call.message.message_id, 
                text=f"🚀 *Respon Server Digiflazz!*\n\nProduk: `{sku}`\nTarget: `{nomor_target}`\nPesan: *{status_transaksi}*\nRC: `{rc_code}`\nRef ID: `{ref_id}`", 
                parse_mode="Markdown"
            )
        except Exception as e:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"❌ Gagal koneksi ke Digiflazz: {str(e)}")

    elif data == "menu_akun":
        bot.send_message(call.message.chat.id, f"👤 *Data Akun*\nUsername: `{DIGIFLAZZ_USERNAME}`\nID Telegram: `{call.from_user.id}`", parse_mode="Markdown")
    elif data == "menu_bantuan":
        bot.send_message(call.message.chat.id, "Cukup kirimkan link produk afiliasi Anda ke chat ini untuk merangkai caption AI.")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Buatkan caption promosi afiliasi yang menarik berdasarkan teks ini: {message.text}"
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Gagal memproses AI: {str(e)}")

@app.route('/webhook', methods=['POST'])
def webhook_terima():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Forbidden', 403

@app.route('/')
def index():
    return "Server Bot PPOB & AI Aktif di Railway!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
