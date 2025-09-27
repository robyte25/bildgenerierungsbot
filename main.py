import os
from io import BytesIO
from PIL import Image
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from g4f.client import Client

# Bot Token aus Environment Variable
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Bildgenerierungs-Funktion
def generiere_und_sende(update: Update, prompt: str):
    try:
        app_client = Client()
        model = app_client.images.generate(model='flux', prompt=prompt, response_format='url')
        image_url = model.data[0].url

        response = requests.get(image_url)
        img_data = BytesIO(response.content)
        pil_img = Image.open(img_data)

        byte_arr = BytesIO()
        pil_img.save(byte_arr, format='PNG')
        byte_arr.seek(0)

        update.message.reply_photo(photo=byte_arr)

    except Exception as e:
        update.message.reply_text(f"Fehler beim Generieren des Bildes: {str(e)}")

def start_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Willkommen! Sende mir ein Prompt, und ich generiere ein Bild daraus. Du kannst auch /prompt verwenden."
    )

def prompt_command(update: Update, context: CallbackContext):
    if context.args:
        prompt = " ".join(context.args)
        update.message.reply_text(f"Generiere Bild für Prompt: {prompt}")
        generiere_und_sende(update, prompt)
    else:
        update.message.reply_text("Bitte gib einen Prompt nach /prompt ein, z. B. /prompt Einhörner im Sonnenuntergang.")

def text_message(update: Update, context: CallbackContext):
    prompt = update.message.text
    update.message.reply_text(f"Generiere Bild für Prompt: {prompt}")
    generiere_und_sende(update, prompt)

def main():
    updater = Updater(token=TELEGRAM_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("prompt", prompt_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, text_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()