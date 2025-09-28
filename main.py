import requests
from io import BytesIO
from PIL import Image
from g4f.client import Client
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# 🔑 Telegram Bot Token
TELEGRAM_TOKEN = "8028466463:AAHW_WIIZFxepl2I-iVyyPG_jtaKJgXaKLk"

# 📩 /start-Befehl
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Willkommen! 👋\nSende mir einfach einen Prompt, und ich generiere ein Bild daraus.\nOder verwende /prompt <dein Text>."
    )

# 📸 /prompt-Befehl
async def prompt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        prompt = " ".join(context.args)
        await update.message.reply_text(f"🎨 Generiere Bild für Prompt: {prompt}")
        await generiere_und_sende(update, prompt)
    else:
        await update.message.reply_text(
            "⚠️ Bitte gib einen Prompt nach /prompt ein, z. B.:\n\n`/prompt Einhörner im Sonnenuntergang`",
            parse_mode="Markdown"
        )

# 🧠 Textnachrichten behandeln
async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    await update.message.reply_text(f"🎨 Generiere Bild für Prompt: {prompt}")
    await generiere_und_sende(update, prompt)

# 🖼️ Bild generieren und senden
async def generiere_und_sende(update: Update, prompt: str):
    try:
        app_client = Client()
        model = app_client.images.generate(
            model='flux',
            prompt=prompt,
            response_format='url'
        )
        image_url = model.data[0].url

        # Lade das Bild herunter
        response = requests.get(image_url)
        img_data = BytesIO(response.content)
        pil_img = Image.open(img_data)

        # In Bytes umwandeln und senden
        byte_arr = BytesIO()
        pil_img.save(byte_arr, format='PNG')
        byte_arr.seek(0)

        await update.message.reply_photo(photo=byte_arr)
    except Exception as e:
        await update.message.reply_text(f"❌ Fehler beim Generieren des Bildes:\n{str(e)}")

# 🚀 Bot starten
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Befehle
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("prompt", prompt_command))

    # Nachrichten
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))

    print("🤖 Bot läuft... Drücke STRG+C zum Stoppen.")
    app.run_polling()

if __name__ == "__main__":
    main()
