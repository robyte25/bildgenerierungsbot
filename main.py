import os
import requests
from io import BytesIO
from PIL import Image
from flask import Flask, request
import telebot
import puter  # Stelle sicher, dass 'puter' in deiner requirements.txt steht

# =============================
# Konfiguration
# =============================
TELEGRAM_TOKEN = "8028466463:AAHW_WIIZFxepl2I-iVyyPG_jtaKJgXaKLk"
WEBHOOK_URL = "https://bildgenerierungsbot-12.onrender.com/webhook"

# Puter Zugangsdaten
PUTER_USER = "RVK"
PUTER_PASS = "Magistralnaja14!"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# =============================
# Bildgenerierung mit Puter
# =============================
def generiere_bild(prompt: str):
    # Authentifizierung bei Puter
    # Wir nutzen hier die Standard-Schnittstelle von Puter
    try:
        # Hinweis: Das puter-SDK handhabt den Login meist über Umgebungsvariablen 
        # oder eine interne .auth() Methode.
        image = puter.ai.txt2img(prompt, test_mode=False)
        
        # Das Ergebnis von puter.ai.txt2img ist direkt ein PIL-Image oder ein Objekt mit .save()
        byte_arr = BytesIO()
        image.save(byte_arr, format='PNG')
        byte_arr.seek(0)
        return byte_arr
    except Exception as e:
        print(f"Puter Fehler: {e}")
        raise e

# =============================
# Telegram Befehle
# =============================
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Hallo! Ich nutze jetzt Puter AI für deine Bilder. Sende mir einfach einen Text.")

@bot.message_handler(commands=['prompt'])
def handle_prompt(message):
    parts = message.text.split(" ", 1)
    if len(parts) == 1:
        bot.send_message(message.chat.id, "⚠️ Bitte gib Text nach /prompt ein.")
        return
    process_request(message, parts[1])

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    process_request(message, message.text)

def process_request(message, prompt):
    bot.send_message(message.chat.id, f"🎨 Puter generiert Bild für: {prompt} ...")
    try:
        bild = generiere_bild(prompt)
        bot.send_photo(message.chat.id, bild)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Fehler bei der Generierung: {e}")

# =============================
# Flask Webhook Endpoint
# =============================
@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return "Forbidden", 403

@app.route("/", methods=["GET"])
def home():
    return "✅ Puter-Bot ist online!"

# =============================
# Start
# =============================
if __name__ == "__main__":
    # Setze Puter Credentials als Umgebungsvariable im laufenden Prozess
    os.environ["PUTER_USERNAME"] = PUTER_USER
    os.environ["PUTER_PASSWORD"] = PUTER_PASS

    # Webhook bei Telegram registrieren
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={WEBHOOK_URL}")
    
    # Flask App starten
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
