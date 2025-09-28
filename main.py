import requests
from io import BytesIO
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
from g4f.client import Client
Filters = filters
# ==== Telegram Token direkt ====
TELEGRAM_TOKEN = "8028466463:AAHW_WIIZFxepl2I-iVyyPG_jtaKJgXaKLk"

def generiere_und_sende(update: Update, prompt: str):
    try:
        client = Client()
        result = client.images.generate(model="flux", prompt=prompt, response_format="url")
        image_url = result.data[0].url

        # Bild synchron herunterladen
        response = requests.get(image_url)
        if response.status_code != 200:
            update.message.reply_text("Fehler beim Herunterladen des Bildes.")
            return

        bio = BytesIO(response.content)
        bio.seek(0)

        # Bild senden
        update.message.reply_photo(photo=bio)

    except Exception as e:
        update.message.reply_text(f"Fehler beim Generieren des Bildes: {e}")

def start_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Willkommen! Sende mir ein Prompt, und ich generiere ein Bild daraus. "
        "Du kannst auch /prompt verwenden."
    )

def prompt_command(update: Update, context: CallbackContext):
    if context.args:
        prompt = " ".join(context.args)
        update.message.reply_text(f"Generiere Bild für Prompt: {prompt}")
        generiere_und_sende(update, prompt)
    else:
        update.message.reply_text("Bitte gib einen Prompt nach /prompt ein.")

def text_message(update: Update, context: CallbackContext):
    prompt = update.message.text
    update.message.reply_text(f"Generiere Bild für Prompt: {prompt}")
    generiere_und_sende(update, prompt)

def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("prompt", prompt_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, text_message))

    print("Bot läuft…")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()