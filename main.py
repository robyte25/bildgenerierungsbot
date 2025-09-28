import os
import requests
from io import BytesIO
from PIL import Image
from flask import Flask, request
import telebot
from g4f.client import Client

# =============================
# Konfiguration
# =============================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8028466463:AAHW_WIIZFxepl2I-iVyyPG_jtaKJgXaKLk")
WEBHOOK_URL = "https://bildgenerierungsbot-12.onrender.com/webhook"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# =============================
# Bildgenerierung
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
# Telegram Befehle
# =============================
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Willkommen! Sende mir einen Prompt oder benutze /prompt <Text>.")

@bot.message_handler(commands=['prompt'])
def handle_prompt(message):
    parts = message.text.split(" ", 1)
    if len(parts) == 1:
        bot.send_message(message.chat.id, "⚠️ Bitte gib nach /prompt einen Text ein.")
        return
    prompt = parts[1]
    bot.send_message(message.chat.id, f"🎨 Generiere Bild für: {prompt} ...")
    try:
        bild = generiere_bild(prompt)
        bot.send_photo(message.chat.id, bild)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Fehler: {e}")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    prompt = message.text
    bot.send_message(message.chat.id, f"🎨 Generiere Bild für: {prompt} ...")
    try:
        bild = generiere_bild(prompt)
        bot.send_photo(message.chat.id, bild)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Fehler: {e}")

# =============================
# Flask Webhook Endpoint
# =============================
@app.route("/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# =============================
# Startseite
# =============================
@app.route("/", methods=["GET"])
def home():
    return "✅ Bot läuft!"

# =============================
# Start
# =============================
if __name__ == "__main__":
    # Webhook setzen
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={WEBHOOK_URL}")
    print("✅ Webhook gesetzt:", WEBHOOK_URL)

    # Flask starten
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
