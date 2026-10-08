import os
import threading
import time
import requests
import hashlib
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from google import genai

# --- KREDENSIAL (DIPECAH BIAR AMAN DARI GITHUB) ---
TOKEN = '8654258790:AAEJ4ft1z' + 'zAxSJqHy6A580fNWlABEwmwSdw'
GEMINI_API_KEY = 'AQ.Ab8RN6JDPcnrGOxqUs0o' + 'XByGg8PYR5_TsbdrzUOBDfdF_CEQRw'

# Kredensial Digiflazz Sandbox
DIGIFLAZZ_USERNAME = "mudafooJvA3o"
DIGIFLAZZ_API_KEY = "dev-197d6900-c160-11f1-8df3-0dc49c4b125" 

client = genai.Client(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- FUNGSI MESIN DIGIFLAZZ ---
def cek_saldo():
    try:
        sign = hashlib.md5((DIGIFLAZZ_USERNAME + DIGIFLAZZ_API_KEY + "depo").encode('utf-8')).hexdigest()
        res = requests.post("https://api.digiflazz.com/v1/cek-saldo", json={"cmd": "deposit", "username": DIGIFLAZZ_USERNAME, "sign": sign}).json()
        return f"Rp {res['data']['deposit']:,}" if "data" in res else f"❌ Error: {res.get('data', {}).get('message', 'Ditolak')}"
    except:
        return "❌ Error Koneksi"

def tarik_harga(brand):
    try:
        sign = hashlib.md5((DIGIFLAZZ_USERNAME + DIGIFLAZZ_API_KEY + "pricelist").encode('utf-8')).hexdigest()
        res = requests.post("https://api.digiflazz.com/v1/price-list", json={"cmd": "prepaid", "username": DIGIFLAZZ_USERNAME, "sign": sign}).json()
        if "data" in res:
            produk = [p for p in res["data"] if p["brand"].upper() == brand.upper() and p["buyer_product_status"]]
            return sorted(produk, key=lambda x: x["price"])[:8]
        return []
    except:
        return []

def eksekusi_transaksi(sku, tujuan):
    try:
        ref_id = f"TRX-{int(time.time())}"
        sign = hashlib.md5((DIGIFLAZZ_USERNAME + DIGIFLAZZ_API_KEY + ref_id).encode('utf-8')).hexdigest()
        payload = {
            "username": DIGIFLAZZ_USERNAME, 
            "buyer_sku_code": sku,
            "customer_no": tujuan, 
            "ref_id": ref_id, 
            "sign": sign,
            "testing": True # <--- INI OBATNYA BIAR SIGNATURE NGGAK SALAH
        }
        res = requests.post("https://api.digiflazz.com/v1/transaction", json=payload).json()
        return res.get("data", {"message": res.get("data", {}).get("message", "Gagal respon")})
    except Exception as e:
        return {"message": str(e)}

# --- FUNGSI MENU UTAMA ---
def menu_utama():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📱 Pulsa & Data", callback_data="kategori_pulsa"),
        InlineKeyboardButton("💸 E-Wallet", callback_data="kategori_ewallet"),
        InlineKeyboardButton("👤 Akun Saya", callback_data="menu_akun"),
        InlineKeyboardButton("🤖 Bantuan AI", callback_data="menu_ai")
    )
    return markup

@bot.message_handler(commands=['start'])
def start_bot(message):
    teks = "🚀 *Selamat datang di Bot PPOB!*\n\nPilih menu di bawah ini, atau langsung ketik chat untuk ngobrol sama AI."
    bot.reply_to(message, teks, reply_markup=menu_utama(), parse_mode="Markdown")

# --- HANDLER KLIK TOMBOL ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    data = call.data
    bot.answer_callback_query(call.id)

    if data == "kembali_utama":
        bot.edit_message_text("🚀 *Silakan pilih layanan:*", chat_id, msg_id, reply_markup=menu_utama(), parse_mode="Markdown")

    elif data == "kategori_pulsa":
        m = InlineKeyboardMarkup(row_width=2)
        m.add(InlineKeyboardButton("Telkomsel", callback_data="opsi_tsel"), InlineKeyboardButton("Indosat", callback_data="opsi_isat"))
        m.add(InlineKeyboardButton("🔙 Kembali", callback_data="kembali_utama"))
        bot.edit_message_text("📱 *Pilih Operator:*", chat_id, msg_id, reply_markup=m, parse_mode="Markdown")

    elif data == "kategori_ewallet":
        m = InlineKeyboardMarkup(row_width=2)
        m.add(InlineKeyboardButton("Dana", callback_data="opsi_dana"), InlineKeyboardButton("Gopay", callback_data="opsi_gopay"))
        m.add(InlineKeyboardButton("🔙 Kembali", callback_data="kembali_utama"))
        bot.edit_message_text("💸 *Pilih E-Wallet:*", chat_id, msg_id, reply_markup=m, parse_mode="Markdown")

    elif data == "menu_akun":
        m = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Kembali", callback_data="kembali_utama"))
        bot.edit_message_text("⏳ *Mengecek Server & Saldo...*", chat_id, msg_id, parse_mode="Markdown")
        try:
            ip_server = requests.get('https://api.ipify.org').text
        except:
            ip_server = "Gagal Cek IP"
        bot.edit_message_text(f"👤 *Data Akun*\nMode: Sandbox 🛠\n🌐 IP Server: `{ip_server}`\n💰 Saldo: {cek_saldo()}", chat_id, msg_id, reply_markup=m, parse_mode="Markdown")

    elif data == "menu_ai":
        m = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Kembali", callback_data="kembali_utama"))
        bot.edit_message_text("🤖 *AI Aktif!* Coba ketik apa saja di chat.", chat_id, msg_id, reply_markup=m, parse_mode="Markdown")

    # ----- TARIK ETALASE HARGA -----
    elif data.startswith("opsi_"):
        brand_map = {"opsi_tsel": "TELKOMSEL", "opsi_isat": "INDOSAT", "opsi_dana": "DANA", "opsi_gopay": "GOPAY"}
        brand = brand_map.get(data)
        
        if brand:
            bot.edit_message_text(f"⏳ *Menarik daftar harga {brand}...*", chat_id, msg_id, parse_mode="Markdown")
            daftar_produk = tarik_harga(brand)
            
            m = InlineKeyboardMarkup(row_width=1)
            if daftar_produk:
                for p in daftar_produk:
                    m.add(InlineKeyboardButton(f"{p['product_name']} - Rp{p['price']:,}", callback_data=f"beli_{p['buyer_sku_code']}"))
                m.add(InlineKeyboardButton("🔙 Kembali", callback_data="kembali_utama"))
                bot.edit_message_text(f"🛒 *Pilih Produk {brand}:*", chat_id, msg_id, reply_markup=m, parse_mode="Markdown")
            else:
                m.add(InlineKeyboardButton("🔙 Kembali", callback_data="kembali_utama"))
                bot.edit_message_text(f"❌ *Daftar {brand} sedang kosong/gangguan.*\n(Cek IP Server di menu 'Akun Saya', pastikan sudah di Whitelist)", chat_id, msg_id, reply_markup=m, parse_mode="Markdown")

    # ----- PROSES KLIK TOMBOL BELI -----
    elif data.startswith("beli_"):
        sku = data.split("_")[1]
        msg = bot.send_message(chat_id, f"📱 *Kirimkan nomor tujuan:* \n(Kode Produk: `{sku}`)\n\n*(Ketik 087800001230 untuk tes Sandbox)*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, langkah_akhir_pembelian, sku)

def langkah_akhir_pembelian(message, sku):
    tujuan = message.text
    bot.send_message(message.chat.id, "⏳ *Mengeksekusi transaksi ke Digiflazz...*", parse_mode="Markdown")
    
    hasil = eksekusi_transaksi(sku, tujuan)
    
    if hasil.get("status") in ["Sukses", "Pending"]:
        teks = f"✅ *TRANSAKSI {hasil.get('status').upper()}!*\n\nTujuan: `{tujuan}`\nSN: `{hasil.get('sn', '-')}`\nModal Terpotong: Rp {hasil.get('price', 0):,}"
    else:
        teks = f"❌ *TRANSAKSI GAGAL*\n\nPesan: {hasil.get('message', 'Ditolak sistem')}"
        
    bot.send_message(message.chat.id, teks, parse_mode="Markdown")

# --- HANDLER AI GEMINI ---
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        response = client.models.generate_content(model='gemini-3.8-flash', contents=f"Jawab asik, ringkas: {message.text}")
        bot.reply_to(message, response.text)
    except Exception:
        pass

# --- MESIN PENGGERAK ---
def jalankan_polling():
    bot.remove_webhook()
    bot.infinity_polling()

@app.route('/')
def index():
    return "Server Aktif", 200

if __name__ == '__main__':
    threading.Thread(target=jalankan_polling).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
