import os
import requests
from io import BytesIO
from flask import Flask, request
import telebot
import puter

# =============================
# Konfiguration
# =============================
TELEGRAM_TOKEN = "8028466463:AAHW_WIIZFxepl2I-iVyyPG_jtaKJgXaKLk"
WEBHOOK_URL = "https://bildgenerierungsbot-12.onrender.com/webhook"

# Liste deiner Puter-Accounts
ACCOUNTS = [
    {"user": "RVK", "pass": "Magistralnaja14!"},
    {"user": "AI1", "pass": Magistralnaja14!"},
    # Du kannst hier beliebig viele Konten hinzufügen
]

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# =============================
# Bildgenerierung mit Fallback
# =============================
def generiere_bild(prompt: str):
    last_error = ""
    
    for account in ACCOUNTS:
        try:
            # Login-Daten für das aktuelle Konto setzen
            os.environ["PUTER_USERNAME"] = account["user"]
            os.environ["PUTER_PASSWORD"] = account["pass"]
            
            print(f"Versuche Generierung mit Account: {account['user']}...")
            
            # Bild generieren
            image = puter.ai.txt2img(prompt, test_mode=False)
            
            # Bild in Speicher schreiben
            byte_arr = BytesIO()
            image.save(byte_arr, format='PNG')
            byte_arr.seek(0)
            return byte_arr # Erfolg! Wir springen aus der Funktion
            
        except Exception as e:
            last_error = str(e)
            if "quota" in last_error.lower():
                print(f"❌ Account {account['user']} hat keine Credits mehr. Wechsle...")
                continue # Nächster Account in der Liste
            else:
                # Ein anderer Fehler (z.B. Netzwerk), wir brechen ab
                raise e
                
    # Wenn alle Accounts durchgelaufen sind und keiner funktioniert hat:
    raise Exception(f"Alle Accounts leer oder Fehler: {last_error}")

# =============================
# Telegram Logik
# =============================
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    prompt = message.text
    if prompt.startswith('/'): return # Ignoriere Befehle hier
    
    bot.send_message(message.chat.id, f"🎨 Generiere mit Puter-Rotation...")
    try:
        bild = generiere_bild(prompt)
        bot.send_photo(message.chat.id, bild)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Abbruch: {e}")

# =============================
# Flask Webhook & Start
# =============================
@app.route("/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def home():
    return "✅ Bot mit Account-Rotation läuft!"

if __name__ == "__main__":
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={WEBHOOK_URL}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
