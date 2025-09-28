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

# 🔑 Telegram Token direkt im Code
TELEGRAM_TOKEN = "8028466463:AAHW_WIIZFxepl2I-iVyyPG_jtaKJgXaKLk"

# ---- Handlers ----
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Willkommen! 👋 Sende mir einen Prompt oder nutze /prompt <text>."
    )

async def prompt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        prompt = " ".join(context.args)
        await update.message.reply_text(f"Generiere Bild für Prompt: {prompt}")
        await generiere_und_sende(update, prompt)
    else:
        await update.message.reply_text(
            "⚠️ Bitte gib einen Prompt nach /prompt ein, z.B. /prompt Einhörner im Sonnenuntergang."
        )

async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    await update.message.reply_text(f"Generiere Bild für Prompt: {prompt}")
    await generiere_und_sende(update, prompt)

async def generiere_und_sende(update: Update, prompt: str):
    try:
        client = Client()
        model = client.images.generate(model='flux', prompt=prompt, response_format='url')
        image_url = model.data[0].url

        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        img_data = BytesIO(response.content)
        pil_img = Image.open(img_data)

        byte_arr = BytesIO()
        pil_img.save(byte_arr, format='PNG')
        byte_arr.seek(0)

        await update.message.reply_photo(photo=byte_arr)
    except Exception as e:
        await update.message.reply_text(f"❌ Fehler beim Generieren des Bildes: {e}")

# ---- Main ----
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Handler registrieren
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("prompt", prompt_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))

    print("🤖 Bot läuft mit Polling...")
    app.run_polling()  # <- Polling statt Webhook

if __name__ == "__main__":
    main()
