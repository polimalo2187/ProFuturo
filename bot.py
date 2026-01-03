import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from config import TELEGRAM_TOKEN, ADMIN_ID
from database import (
    registrar_usuario,
    usuario_activo,
    es_primera_vez,
    marcar_bienvenida_enviada
)
from ai_engine import responder
from voice_engine import generar_audio, eliminar_audio
from admin_panel import (
    panel_admin,
    ver_alumnos,
    activar_alumno,
    desactivar_alumno,
    procesar_id_admin
)

# =========================
# COMANDOS INICIALES
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    registrado = registrar_usuario(user.id, user.first_name, user.username or "")

    if not usuario_activo(user.id):
        await update.message.reply_text(
            "🚫 No formas parte de la academia actualmente.\n"
            "Contacta con tu profesor para activarte."
        )
        return

    # Solo enviar mensaje de bienvenida si es la primera vez que entra
    if es_primera_vez(user.id):
        mensaje_bienvenida = (
            "Bienvenido a Crono Assistant. "
            "Soy tu asesor personal de trading disponible 24/7. "
            "Puedo ayudarte a entender gráficos, conceptos y escenarios de trading. "
            "Recuerda: esto es contenido educativo y no asesoría financiera."
        )
        # Enviar audio
        audio = generar_audio(mensaje_bienvenida)
        with open(audio, "rb") as voz:
            await update.message.reply_voice(voice=voz)
        # Enviar texto
        await update.message.reply_text(mensaje_bienvenida)
        eliminar_audio(audio)
        # Marcar que ya recibió bienvenida
        marcar_bienvenida_enviada(user.id)

# =========================
# MENSAJES DE ALUMNOS
# =========================

async def mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not usuario_activo(user_id):
        await update.message.reply_text("🚫 Acceso no activo.")
        return

    texto_usuario = update.message.text

    # Llamar IA para generar respuesta
    respuesta = responder(user_id, texto_usuario)

    # Enviar audio de la respuesta
    audio = generar_audio(respuesta)
    with open(audio, "rb") as voz:
        await update.message.reply_voice(voice=voz)
    eliminar_audio(audio)

    # Enviar texto
    await update.message.reply_text(respuesta)

# =========================
# MENSAJES DE ADMIN
# =========================

async def mensajes_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return
    await procesar_id_admin(update, context)

# =========================
# IMÁGENES (GRÁFICAS)
# =========================

async def imagenes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not usuario_activo(user_id):
        await update.message.reply_text("🚫 Acceso no activo.")
        return

    photo_file = await update.message.photo[-1].get_file()
    path_local = f"{user_id}_grafica.png"
    await photo_file.download_to_drive(path_local)

    mensaje_respuesta = (
        "✅ Imagen recibida. \n"
        "Analizando desde perspectiva educativa...\n"
        "Recuerda: esto es un ejemplo educativo, no una recomendación financiera."
    )

    audio = generar_audio(mensaje_respuesta)
    with open(audio, "rb") as voz:
        await update.message.reply_voice(voice=voz)
    eliminar_audio(audio)

    await update.message.reply_text(mensaje_respuesta)

    os.remove(path_local)

# =========================
# INICIALIZACIÓN DEL BOT
# =========================

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Comando /start
    app.add_handler(CommandHandler("start", start))

    # Panel admin
    app.add_handler(CommandHandler("admin", panel_admin))

    # Panel admin botones
    app.add_handler(CallbackQueryHandler(ver_alumnos, pattern="admin_ver"))
    app.add_handler(CallbackQueryHandler(activar_alumno, pattern="admin_activar"))
    app.add_handler(CallbackQueryHandler(desactivar_alumno, pattern="admin_desactivar"))

    # Mensajes admin (solo de ADMIN_ID)
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID),
        mensajes_admin
    ))

    # Mensajes alumnos (todos los demás usuarios)
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.User(ADMIN_ID),
        mensajes
    ))

    # Mensajes con imágenes
    app.add_handler(MessageHandler(filters.PHOTO, imagenes))

    # Ejecutar bot
    app.run_polling()

if __name__ == "__main__":
    main()
