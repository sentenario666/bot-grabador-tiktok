import telebot
import subprocess
import os
from flask import Flask

# ---------- PON TU TOKEN AQUÍ ----------
TOKEN = "8941299155:AAEUE2wO7FF-VGickwM0TVYYzDPcvzp4VyI"
bot = telebot.TeleBot(TOKEN)

# ---------- COMANDO /START ----------
@bot.message_handler(commands=['start'])
def bienvenida(mensaje):
    bot.reply_to(mensaje, "👋 Hola! Envíame un enlace de Bigo Live, Kick o Clapper y grabaré la transmisión.")

# ---------- GRABAR TRANSMISIÓN ----------
@bot.message_handler(func=lambda msg: True)
def grabar(mensaje):
    url = mensaje.text.strip()
    
    if not any(sitio in url for sitio in ['bigo.tv', 'kick.com', 'clapperapp.com']):
        bot.reply_to(mensaje, "❌ Solo acepto enlaces de Bigo Live, Kick y Clapper")
        return
    
    bot.reply_to(mensaje, "🎬 Recibido... iniciando grabación ⏳")
    
    nombre_archivo = "grabacion.mp4"
    comando = ["yt-dlp", "-o", nombre_archivo, "--no-check-certificates", url]
    
    try:
        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=600)
        
        if os.path.exists(nombre_archivo) and os.path.getsize(nombre_archivo) > 0:
            bot.reply_to(mensaje, "✅ Grabación lista! Enviando archivo...")
            with open(nombre_archivo, 'rb') as f:
                bot.send_document(mensaje.chat.id, f)
            os.remove(nombre_archivo)
        else:
            bot.reply_to(mensaje, "⚠️ No se pudo grabar. La transmisión podría estar privada o ya terminó")
            
    except Exception as e:
        bot.reply_to(mensaje, f"❌ Error: {str(e)}")

# ---------- SERVIDOR PARA RENDER ----------
app = Flask(__name__)

@app.route('/')
def estado():
    return "✅ Bot activo y funcionando correctamente!"

# ---------- INICIAR TODO ----------
if __name__ == "__main__":
    from threading import Thread
    
    def arrancar_bot():
        bot.infinity_polling()
    
    Thread(target=arrancar_bot, daemon=True).start()
    
    puerto = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=puerto)


