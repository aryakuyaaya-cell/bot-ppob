import os
import threading
import telebot
from flask import Flask
from google import genai

# --- KREDENSIAL ---
TOKEN = '8654258790:AAEz8WelOJrqxRHXU3iY6r3vhW0mwaZNcSA'
GEMINI_API_KEY = 'AQ.Ab8RN6IqzTlrvnBaghoVDi9bYXo9NW2VX4T9JF9wJgc7_mkggQ'

client = genai.Client(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.reply_to(message, "🔥 Akhirnya nyaut! Bot berhasil tembus pakai jalur Polling.\n\nCoba kirimkan pertanyaan apa saja untuk ngetes AI Gemini:")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Jawab dengan asik dan ringkas: {message.text}"
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Waduh AI error: {str(e)}")

# Fungsi untuk bot menjemput bola (Polling)
def jalankan_polling():
    # Hapus paksa webhook yang nyangkut di sistem Telegram
    bot.remove_webhook()
    # Mulai menarik data
    bot.infinity_polling()

# Rute web pancingan biar Railway nggak ngira servernya mati
@app.route('/')
def index():
    return "Server Pancingan Aktif! (Bot berjalan di background)", 200

if __name__ == '__main__':
    # 1. Jalankan bot di layar belakang (thread terpisah)
    thread = threading.Thread(target=jalankan_polling)
    thread.start()
    
    # 2. Jalankan pancingan web server untuk Railway
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
