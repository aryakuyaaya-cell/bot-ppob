import os
import requests
from flask import Flask, request

TOKEN = '8654258790:AAEz8WelOJrqxRHXU3iY6r3vhW0mwaZNcSA'
app = Flask(__name__)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

def kirim_pesan(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route('/webhook', methods=['POST'])
def webhook_terima():
    try:
        data = request.get_json(force=True)
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")
            kirim_pesan(chat_id, f"Bot nyaut! Pesan diterima: {text}")
        return '', 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return '', 200

@app.route('/')
def index():
    return "Server Aktif!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
