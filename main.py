import os
import telebot
import yt_dlp
from datetime import datetime
import queue
import threading

# 🔑 PON TU TOKEN AQUÍ (de @BotFather)
TOKEN = "8941299155:AAEUE2wO7FF-VGickwM0TVYYzDPcvzp4VyI"
bot = telebot.TeleBot(TOKEN)

# 📋 COLA — atiende de a uno, sin chocar
cola_tareas = queue.Queue()

def trabajador():
    while True:
        mensaje = cola_tareas.get()
        try:
            procesar_mensaje(mensaje)
        except Exception as e:
            bot.reply_to(mensaje, f"❌ Error: {str(e)}")
        finally:
            cola_tareas.task_done()

# ▶️ Iniciar la cola en segundo plano
hilo = threading.Thread(target=trabajador, daemon=True)
hilo.start()

def procesar_mensaje(message):
    url = message.text.strip()
    usuario = message.from_user.username or f"usuario_{message.from_user.id}"
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ❌ No es TikTok
    if "tiktok.com" not in url:
        bot.reply_to(message, "❌ Envíame un enlace de TikTok")
        return

    # 🔴 ES EN VIVO
    if "/live" in url or "live.tiktok.com" in url:
        bot.reply_to(message, f"🔴 EN VIVO DETECTADO\n👤 Usuario: @{usuario}\n✅ Grabando en MÁXIMA CALIDAD...\n⏳ Te lo envío al terminar!")
        
        nombre_archivo = f"live_{usuario}_{fecha}.mp4"
        
        opts_live = {
            "format": "best",  # 🔥 MÁXIMA CALIDAD
            "outtmpl": nombre_archivo,
            "quiet": False,
            "no_warnings": True,
            "format_sort": ["filesize:1800M"]  # ✅ No pasa de 1.8 GB
        }
        
        with yt_dlp.YoutubeDL(opts_live) as ydl:
            ydl.download([url])
        
        # Enviar
        with open(nombre_archivo, "rb") as f:
            bot.send_video(message.chat.id, f, caption=f"✅ Grabación lista\n📁 {nombre_archivo}")
        
        # 🧹 BORRAR SOLO
        os.remove(nombre_archivo)
        return

    # 📹 VIDEO NORMAL
    bot.reply_to(message, f"🔽 Descargando en MÁXIMA CALIDAD...\n👤 Usuario: @{usuario}")
    
    nombre_archivo = f"video_{usuario}_{fecha}.mp4"
    
    opts = {
        "format": "best",  # 🔥 MÁXIMA CALIDAD
        "outtmpl": nombre_archivo,
        "no_warnings": True,
        "format_sort": ["filesize:1800M"]
    }
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    
    # Enviar
    with open(nombre_archivo, "rb") as f:
        bot.send_video(message.chat.id, f, caption=f"✅ Listo\n📁 {nombre_archivo}")
    
    # 🧹 BORRAR SOLO
    os.remove(nombre_archivo)

# 📬 Recibir mensajes y poner en COLA
@bot.message_handler(func=lambda message: True)
def recibir(message):
    cola_tareas.put(message)
    if cola_tareas.qsize() > 1:
        bot.reply_to(message, f"✅ En cola — hay {cola_tareas.qsize()} antes que tú, te atiendo enseguida!")

# Comandos
@bot.message_handler(commands=['start', 'help'])
def bienvenida(message):
    bot.reply_to(message, "👋 ¡Hola! Soy tu bot personal\n🔴 Enlaces de live → grabo y te envío\n📹 Videos normales → descargo en máxima calidad\n✅ Te atiendo a ti solo o con más gente, en orden")

# Iniciar
bot.polling(none_stop=True)
# Servidor web mínimo para que Render no se queje
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot funcionando!"

if __name__ == "__main__":
    import os
    PORT = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=PORT)

