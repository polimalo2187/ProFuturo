from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from utils import registrar_usuario, guardar_wallet, actualizar_pago
from config import TOKEN

# Estado temporal de usuarios
USER_STATE = {}

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await update.message.reply_text(
        "¡Bienvenido al curso de Trading de Futuros Perpetuos!\n"
        "Por favor, envía tu nombre completo para registrarte."
    )
    USER_STATE[user_id] = "esperando_nombre"

# Manejo de mensajes de usuario
async def mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    texto = update.message.text

    if USER_STATE.get(user_id) == "esperando_nombre":
        registrado = registrar_usuario(user_id, texto)
        if registrado:
            await update.message.reply_text(f"¡Gracias {texto}! Ahora envía tu wallet USDT BEP-20.")
            USER_STATE[user_id] = "esperando_wallet"
        else:
            await update.message.reply_text("Ya estás registrado. Por favor envía tu wallet USDT BEP-20.")
            USER_STATE[user_id] = "esperando_wallet"

    elif USER_STATE.get(user_id) == "esperando_wallet":
        guardar_wallet(user_id, texto)
        await update.message.reply_text(
            f"Wallet registrada: {texto}\nAhora espera la verificación del pago."
        )
        USER_STATE[user_id] = "esperando_pago"

        # Simulación de pago confirmado
        actualizar_pago(user_id)
        await update.message.reply_text("¡Pago confirmado! Enviando tu primera lección...")
        await enviar_primera_leccion(update, context)
        USER_STATE[user_id] = "curso_iniciado"

# Función para enviar primera lección
async def enviar_primera_leccion(update, context):
    # Audio
    audio_path = "lecciones/01/audio.mp3"
    await context.bot.send_audio(chat_id=update.message.chat_id, audio=InputFile(audio_path))

    # Texto
    with open("lecciones/01/texto.md", "r", encoding="utf-8") as f:
        texto = f.read()
    await context.bot.send_message(chat_id=update.message.chat_id, text=texto)

# Inicializar bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje))

app.run_polling()
