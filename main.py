import os
import requests
from io import BytesIO
from PIL import Image
from flask import Flask, request
from g4f.client import Client
from telegram import Bot, Update

# =============================
# Konfiguration
# =============================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8028466463:AAHW_WIIZFxepl2I-iVyyPG_jtaKJgXaKLk")
WEBHOOK_URL = "https://bildgenerierungsbot-12.onrender.com/webhook"

bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

# =============================
# Webhook Setup
# =============================
def set_webhook():
    resp = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
        data={"url": WEBHOOK_URL}
    )
    print("Webhook Response:", resp.json())

# =============================
# Bildgenerierung (synchronisiert)
# =============================
def generiere_bild(prompt: str):
    client = Client()
    model = client.images.generate(model='flux', prompt=prompt, response_format='url')
    image_url = model.data[0].url

    response = requests.get(image_url)
    pil_img = Image.open(BytesIO(response.content))

    byte_arr = BytesIO()
    pil_img.save(byte_arr, format='PNG')
    byte_arr.seek(0)
    return byte_arr

# =============================
# Telegram Webhook Handler
# =============================
@app.route("/webhook", methods=["POST"])
def webhook():
    update_data = request.get_json()
    update = Update.de_json(update_data, bot)

    if update.message:
        chat_id = update.message.chat.id
        text = update.message.text

        if text.startswith("/start"):
            bot.send_message(chat_id, "Willkommen! Schicke mir einen Prompt, ich generiere ein Bild daraus.")
        elif text.startswith("/prompt"):
            prompt = " ".join(text.split()[1:])
            if not prompt:
                bot.send_message(chat_id, "Bitte gib einen Prompt nach /prompt ein.")
            else:
                bot.send_message(chat_id, f"🎨 Generiere Bild für Prompt: {prompt} …")
                try:
                    bild = generiere_bild(prompt)
                    bot.send_photo(chat_id, photo=bild)
                except Exception as e:
                    bot.send_message(chat_id, f"❌ Fehler: {e}")
        else:
            bot.send_message(chat_id, f"🎨 Generiere Bild für Prompt: {text} …")
            try:
                bild = generiere_bild(text)
                bot.send_photo(chat_id, photo=bild)
            except Exception as e:
                bot.send_message(chat_id, f"❌ Fehler: {e}")

    return "OK"

# =============================
# Optionale Startseite (gegen 404)
# =============================
@app.route("/")
def home():
    return "✅ Telegram Bildgenerierungsbot läuft!"

# =============================
# Start
# =============================
if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
