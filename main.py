import os
from io import BytesIO
from PIL import Image, UnidentifiedImageError
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
from g4f.client import Client

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def generiere_und_sende(update: Update, prompt: str):
    try:
        app_client = Client()
        model = app_client.images.generate(model='flux', prompt=prompt, response_format='url')
        image_url = model.data[0].url

        response = requests.get(image_url)
        img_data = BytesIO(response.content)

        try:
            pil_img = Image.open(img_data)
        except UnidentifiedImageError:
            update.message.reply_text("Fehler: Konnte das Bild nicht öffnen.")
            return

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
        update.message.reply_text("Bitte gib einen Prompt nach /prompt ein.")

def text_message(update: Update, context: CallbackContext):
    prompt = update.message.text
    update.message.reply_text(f"Generiere Bild für Prompt: {prompt}")
    generiere_und_sende(update, prompt)

def main():
    updater = Updater(token=TELEGRAM_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("prompt", prompt_command))
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()