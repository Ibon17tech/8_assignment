import os
import threading
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

app = Flask(__name__)

# Sozlamalar
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# --- 1. BOT XABARLARIGA JAVOB BERISH QISMI ---
def bot_polling():
    """Botga kelgan xabarlarni tekshirish va javob qaytarish"""
    last_update_id = 0
    print("Bot xabarlarni kutmoqda...")
    
    while True:
        try:
            # Telegramdan yangi xabarlarni olish
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            params = {"offset": last_update_id + 1, "timeout": 30}
            response = requests.get(url, params=params).json()

            if response.get("result"):
                for update in response["result"]:
                    last_update_id = update["update_id"]
                    if "message" in update:
                        chat_id = update["message"]["chat"]["id"]
                        text = update["message"].get("text", "")

                        # Agar foydalanuvchi /start bossa
                        if text == "/start":
                            send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                            msg_payload = {
                                "chat_id": chat_id, 
                                "text": "Hello, what will we do?"
                            }
                            requests.post(send_url, data=msg_payload)
        except Exception as e:
            print(f"Bot error: {e}")

# --- 2. WEB SAYT QISMI ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    phone = request.form.get('full_phone')
    travel_date = request.form.get('travel_date')
    guests = request.form.get('guests')
    
    message_text = (
        "🏛️ *NEW GLOBAL BOOKING: YANGIYUL*\n\n"
        f"👤 *Client:* {first_name} {last_name}\n"
        f"📞 *Phone:* `{phone}`\n"
        f"📅 *Date:* {travel_date}\n"
        f"📍 *Destination:* Yangiyul City Tour\n"
        f"👥 *Guests:* {guests}\n"
        "--------------------------\n"
        "✅ *Action:* Contact the client via WhatsApp/Telegram"
    )
    
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message_text, "parse_mode": "Markdown"}
    
    try:
        requests.post(telegram_url, data=payload)
        return """
            <body style="font-family:sans-serif; text-align:center; padding-top:100px; background:#f4f7f6;">
                <h1 style="color:#2d3436;">Booking Successful! ✅</h1>
                <p>We have received your request. See you in Yangiyul!</p>
                <a href="/" style="color:#ff7675; text-decoration:none; font-weight:bold;">← Go Back</a>
            </body>
        """
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    # 1. Botni alohida oqimda ishga tushiramiz
    t = threading.Thread(target=bot_polling)
    t.daemon = True
    t.start()
    
    # 2. Render portni o'zi beradi, shuni olamiz
    port = int(os.environ.get("PORT", 5000))
    
    # 3. FAQAT BITTA app.run bo'lishi kerak!
    # Render-da debug=False bo'lgani ma'qul
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)