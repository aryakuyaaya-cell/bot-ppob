import os
import hashlib
import requests
from google import genai
from flask import Flask, request

# --- DATA KREDENSIAL ---
TOKEN = '8654258790:AAEz8WelOJrqxRHXU3iY6r3vhW0mwaZNcSA'
GEMINI_API_KEY = 'AQ.Ab8RN6IqzTlrvnBaghoVDi9bYXo9NW2VX4T9JF9wJgc7_mkggQ'

# Kredensial Digiflazz Sandbox
DIGIFLAZZ_USERNAME = "mudafooJvA3o"
DIGIFLAZZ_API_KEY = "dev-197d6900-c160-11f1-8df3-0dc49c4b125"
DIGIFLAZZ_URL = "https://api.digiflazz.com/v1/transaction"

# Inisialisasi Gemini
client = genai.Client(api_key=GEMINI_API_KEY)
app = Flask(__name__)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

def kirim_pesan(chat_id, text, reply_markup=None):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(url, json=payload)

@app.route('/webhook', methods=['POST'])
def webhook_terima():
    try:
        data = request.get_json(force=True)
        
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")
            
            if text.startswith("/start"):
                menu = {
                    "inline_keyboard": [
                        [{"text": "🛍 Layanan PPOB", "callback_data": "menu_ppob"}],
                        [{"text": "💡 Bantuan AI Gemini", "callback_data": "menu_bantuan"}]
                    ]
                }
                kirim_pesan(chat_id, "Halo! Selamat datang di *Asisten PPOB & AI*. 🚀\n\nKirimkan teks atau pertanyaan apa saja untuk dijawab AI:", menu)
            else:
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=f"Jawab dengan ringkas dan menarik: {text}"
                    )
                    kirim_pesan(chat_id, response.text)
                except Exception as ai_err:
                    kirim_pesan(chat_id, f"Gagal memproses AI: {str(ai_err)}")

        elif "callback_query" in data:
            callback = data["callback_query"]
            chat_id = callback["message"]["chat"]["id"]
            callback_data = callback["data"]
            
            if callback_data == "menu_ppob":
                kirim_pesan(chat_id, "🛠 *Menu PPOB Sandbox*\nFitur transaksi siap digunakan.")
            elif callback_data == "menu_bantuan":
                kirim_pesan(chat_id, "Kirimkan pesan apa saja ke bot ini, AI akan otomatis membalasnya.")

        return '', 200
    except Exception as e:
        print(f"Error handling webhook: {str(e)}")
        return '', 200

@app.route('/')
def index():
    return "Server Bot PPOB & AI Aktif Mulus!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
