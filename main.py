import telebot
import subprocess
import os
import re
from flask import Flask

# ==============================================
# 🔑 PON TU TOKEN DE BOTFATHER AQUÍ
# ==============================================
TOKEN = "8941299155:AAEUE2wO7FF-VGickwM0TVYYzDPcvzp4VyI"
bot = telebot.TeleBot(TOKEN)

# ==============================================
# 👋 MENSAJE DE BIENVENIDA
# ==============================================
@bot.message_handler(commands=['start'])
def bienvenida(mensaje):
    bot.reply_to(mensaje, 
        "👋 ¡Hola! Soy tu Grabador de TikTok 📹\n\n"
        "Solo mándame el **nombre del creador**\n"
        "Ejemplo: @nombre_canal o solo el nombre\n\n"
        "Yo busco la transmisión en vivo y la grabo ✅"
    )

# ==============================================
# 🔗 CONSTRUIR ENLACE DESDE EL NOMBRE
# ==============================================
def obtener_enlace_tiktok(texto):
    texto = texto.strip()
    
    # Si ya puso @, lo limpiamos
    if texto.startswith('@'):
        usuario = texto[1:]
    # Si escribió el enlace completo
    elif 'tiktok.com' in texto:
        return texto
    # Si solo escribió el nombre
    else:
        usuario = texto
    
    # Devolvemos el enlace directo a su perfil en vivo
    return f"https://www.tiktok.com/@{usuario}/live"

# ==============================================
# 🎬 GRABAR POR NOMBRE
# ==============================================
@bot.message_handler(func=lambda msg: True)
def grabar_por_nombre(mensaje):
    texto_recibido = mensaje.text.strip()
    
    # Ignorar comandos
    if texto_recibido.startswith('/'):
        return
    
    bot.reply_to(mensaje, f"🔍 Buscando a: {texto_recibido}... ⏳")
    
    url = obtener_enlace_tiktok(texto_recibido)
    nombre_archivo = "grabacion_tiktok.mp4"
    
    # Comando para buscar y descargar
    comando = [
        "yt-dlp",
        "--no-playlist",
        "--no-check-certificates",
        "--live-from-start",
        "-f", "best",
        "-o", nombre_archivo,
        url
    ]
    
    try:
        bot.reply_to(mensaje, "📡 Encontrado! Iniciando grabación... puede tardar varios minutos ⏳")
        
        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=3600)
        
        if os.path.exists(nombre_archivo) and os.path.getsize(nombre_archivo) > 50000:
            bot.reply_to(mensaje, "✅ ¡Grabación lista! Enviando archivo... 📤")
            with open(nombre_archivo, 'rb') as f:
                bot.send_document(mensaje.chat.id, f)
            os.remove(nombre_archivo)
        else:
            bot.reply_to(mensaje, 
                "⚠️ No se pudo grabar. Posibles causas:\n"
                "🔸 El usuario NO está en vivo ahora\n"
                "🔸 El nombre está mal escrito\n"
                "🔸 La transmisión es privada\n"
                "🔸 TikTok bloqueó el acceso\n\n"
                "Vuelve a intentar cuando esté en vivo 📹"
            )
            
    except Exception as e:
        bot.reply_to(mensaje, f"❌ Error: {str(e)}")

# ==============================================
# 🌐 SERVIDOR PARA RENDER
# ==============================================
app = Flask(__name__)

@app.route('/')
def estado():
    return "✅ Grabador de TikTok — Activo y funcionando!"

# ==============================================
# 🚀 INICIAR BOT
# ==============================================
if __name__ == "__main__":
    from threading import Thread
    
    def arrancar_bot():
        bot.infinity_polling()
    
    Thread(target=arrancar_bot, daemon=True).start()
    
    puerto = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=puerto)






