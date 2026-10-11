import telebot
import subprocess
import os
import re
from flask import Flask

# ==============================================
# 🔑 CONFIGURACIÓN - PON TU TOKEN AQUÍ
# ==============================================
TOKEN = "8941299155:AAEUE2wO7FF-VGickwM0TVYYzDPcvzp4VyI"
bot = telebot.TeleBot(TOKEN)

# ==============================================
# 👋 MENSAJE DE BIENVENIDA
# ==============================================
@bot.message_handler(commands=['start'])
def bienvenida(mensaje):
    bot.reply_to(mensaje, "👋 ¡Hola! Soy tu Grabador de Lives 🎬\n\nEnvíame un enlace y grabaré de:\n✅ Bigo Live\n✅ Kick\n✅ Clapper\n✅ TikTok\n✅ Tango Live\n✅ Twitch")

# ==============================================
# 🧹 LIMPIAR ENLACES (especialmente TikTok)
# ==============================================
def limpiar_enlace(url):
    url = url.strip()
    if 'tiktok.com' in url:
        match = re.search(r'(https?://[^\s]+tiktok\.com/[^\s?]+)', url)
        if match:
            return match.group(1)
    return url

# ==============================================
# 🎬 FUNCIÓN PRINCIPAL DE GRABACIÓN
# ==============================================
@bot.message_handler(func=lambda msg: True)
def grabar_transmision(mensaje):
    url_entrada = mensaje.text.strip()
    url = limpiar_enlace(url_entrada)
    
    # Plataformas soportadas
    plataformas = ['bigo.tv', 'kick.com', 'clapperapp.com', 'tiktok.com', 'tango.live', 'twitch.tv']
    
    if not any(sitio in url for sitio in plataformas):
        bot.reply_to(mensaje, "❌ Solo acepto enlaces de:\n✅ Bigo Live\n✅ Kick\n✅ Clapper\n✅ TikTok\n✅ Tango Live\n✅ Twitch")
        return
    
    bot.reply_to(mensaje, "🎬 Recibido... iniciando grabación ⏳\nEsto puede tardar unos minutos...")
    
    nombre_archivo = "grabacion.mp4"
    
    # Comando mejorado
    comando = [
        "yt-dlp",
        "--no-playlist",
        "--no-check-certificates",
        "--socket-timeout", "300",
        "-f", "best",
        "-o", nombre_archivo,
        url
    ]
    
    try:
        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=1800)
        
        if os.path.exists(nombre_archivo) and os.path.getsize(nombre_archivo) > 10000:
            bot.reply_to(mensaje, "✅ ¡Grabación lista! Enviando archivo... 📤")
            with open(nombre_archivo, 'rb') as f:
                bot.send_document(mensaje.chat.id, f)
            os.remove(nombre_archivo)
        else:
            bot.reply_to(mensaje, "⚠️ No se pudo grabar. Posibles causas:\n🔸 La transmisión ya terminó\n🔸 Es privada o requiere inicio de sesión\n🔸 TikTok bloqueó el acceso\n\nIntenta con un enlace que esté EN VIVO ahora 📹")
            
    except Exception as e:
        bot.reply_to(mensaje, f"❌ Error: {str(e)}")

# ==============================================
# 🌐 SERVIDOR PARA QUE RENDER NO SE QUEJE
# ==============================================
app = Flask(__name__)

@app.route('/')
def estado():
    return "✅ Grabador de Lives — Activo y funcionando!"

# ==============================================
# 🚀 INICIAR TODO
# ==============================================
if __name__ == "__main__":
    from threading import Thread
    
    def arrancar_bot():
        bot.infinity_polling()
    
    Thread(target=arrancar_bot, daemon=True).start()
    
    puerto = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=puerto)





