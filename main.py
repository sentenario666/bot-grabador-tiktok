import telebot
import subprocess
import os
import threading

# ==============================================
# 🔑 PON TU TOKEN DE @BotFather AQUÍ
# ==============================================
TOKEN = "8941299155:AAEUE2wO7FF-VGickwM0TVYYzDPcvzp4VyI"
bot = telebot.TeleBot(TOKEN)

# Variable para controlar la grabación
proceso_grabacion = None

# ==============================================
# 👋 BIENVENIDA
# ==============================================
@bot.message_handler(commands=['start'])
def bienvenida(mensaje):
    bot.reply_to(mensaje,
        "📹 **Grabador de TikTok**\n\n"
        "Mándame el nombre del usuario (con o sin @)\n"
        "Ejemplo: `usuario123` o `@usuario123`\n\n"
        "Comandos disponibles:\n"
        "⏹ /detener → Para la grabación en curso"
    )

# ==============================================
# ⏹ DETENER GRABACIÓN
# ==============================================
@bot.message_handler(commands=['detener'])
def detener(mensaje):
    global proceso_grabacion
    if proceso_grabacion and proceso_grabacion.poll() is None:
        proceso_grabacion.terminate()
        proceso_grabacion.wait()
        bot.reply_to(mensaje, "⏹ **Grabación detenida** por tu orden ✅")
        proceso_grabacion = None
    else:
        bot.reply_to(mensaje, "ℹ️ No hay ninguna grabación en curso")

# ==============================================
# 🎬 FUNCIÓN DE GRABACIÓN
# ==============================================
def grabar(mensaje, usuario):
    global proceso_grabacion
    
    url = f"https://www.tiktok.com/@{usuario}/live"
    nombre_archivo = f"tiktok_{usuario}.mp4"
    
    bot.reply_to(mensaje, f"🔍 Buscando a: @{usuario}... ⏳")
    
    # Comando de grabación
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
        bot.reply_to(mensaje,
            "📡 Encontrado! Iniciando grabación... ⏳\n"
            "Puede tardar varios minutos, ten paciencia 😊\n"
            "Usa /detener si quieres parar"
        )
        
        proceso_grabacion = subprocess.Popen(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Esperar a que termine
        proceso_grabacion.wait()
        
        # Verificar si fue detenido
        if proceso_grabacion.returncode == -15:
            if os.path.exists(nombre_archivo):
                os.remove(nombre_archivo)
            return
        
        if os.path.exists(nombre_archivo) and os.path.getsize(nombre_archivo) > 50000:
            bot.reply_to(mensaje, "✅ **¡Grabación lista!** Enviando archivo... 📤")
            with open(nombre_archivo, 'rb') as f:
                bot.send_document(mensaje.chat.id, f)
            os.remove(nombre_archivo)
        else:
            bot.reply_to(mensaje,
                "⚠️ No se pudo grabar. Posibles causas:\n"
                "🔸 El usuario NO está en vivo ahora\n"
                "🔸 Nombre mal escrito\n"
                "🔸 Transmisión privada o protegida\n"
                "🔸 TikTok bloqueó el acceso\n\n"
                "Vuelve a intentar cuando esté en vivo 📹"
            )
            
    except Exception as e:
        bot.reply_to(mensaje, f"❌ Error: {str(e)}")
    finally:
        proceso_grabacion = None

# ==============================================
# 📩 RECIBIR MENSAJES
# ==============================================
@bot.message_handler(func=lambda msg: True)
def recibir(mensaje):
    global proceso_grabacion
    
    texto = mensaje.text.strip()
    
    # Ignorar comandos
    if texto.startswith('/'):
        return
    
    # Si ya hay una grabación en curso
    if proceso_grabacion and proceso_grabacion.poll() is None:
        bot.reply_to(mensaje, "⚠️ Ya hay una grabación en curso. Usa /detener primero")
        return
    
    # Limpiar nombre
    usuario = texto.lstrip('@')
    
    # Iniciar grabación en segundo plano
    threading.Thread(target=grabar, args=(mensaje, usuario), daemon=True).start()

# ==============================================
# 🚀 INICIAR BOT
# ==============================================
if __name__ == "__main__":
    print("✅ Bot de TikTok activo!")
    bot.infinity_polling()







