
from flask import Flask, request
import telebot
import yt_dlp
import os

app = Flask(__name__)

# Tu token de Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def bienvenida(message):
    bot.reply_to(message, "👋 ¡Hola! Envíame un enlace de TikTok y te lo descargo 📥")

@bot.message_handler(func=lambda message: True)
def descargar_tiktok(message):
    url = message.text
    if "tiktok.com" not in url:
        bot.reply_to(message, "❌ Por favor envíame un enlace de TikTok")
        return
    
    bot.reply_to(message, "🔄 Descargando... un momento ⏳")
    
    try:
        # Configuración de descarga
        opts = {
            'format': 'best',
            'outtmpl': 'video.mp4',
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        
        # Enviar el video
        with open('video.mp4', 'rb') as f:
            bot.send_video(message.chat.id, f)
        
        # Borrar el archivo después de enviar
        os.remove('video.mp4')
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error al descargar: {str(e)}")

# Webhook para Render
@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return "OK", 200

@app.route('/')
def index():
    return "✅ Bot funcionando!"

if __name__ == "__main__":
    # Configurar webhook
    RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
    if RENDER_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_URL}/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
