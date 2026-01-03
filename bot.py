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
from database import registrar_usuario, usuario_activo
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
    registrar_usuario(user.id, user.first_name, user.username or "")
    
    if not usuario_activo(user.id):
        await update.message.reply_text(
            "🚫 No formas parte de la academia actualmente.\n"
            "Contacta con tu profesor para activarte."
        )
        return

    # Mensaje de bienvenida
    mensaje_bienvenida = (
        "Bienvenido a Crono Assistant. "
        "Soy tu asesor personal de trading disponible 24/7. "
        "Puedo ayudarte a entender gráficos, conceptos y escenarios de trading. "
        "Recuerda: esto es contenido educativo y no asesoría financiera."
    )

    # Enviar audio de bienvenida
    audio = generar_audio(mensaje_bienvenida)
    with open(audio, "rb") as voz:
        await update.message.reply_voice(voice=voz)
    eliminar_audio(audio)

    # Enviar texto de bienvenida
    await update.message.reply_text(mensaje_bienvenida)

# =========================
# MENSAJES DE ALUMNOS
# =========================

async def mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not usuario_activo(user_id):
        await update.message.reply_text("🚫 Acceso no activo.")
        return

    # Obtener texto del alumno
    texto_usuario = update.message.text

    # Responder con IA
    respuesta = responder(user_id, texto_usuario)

    # Enviar audio de la respuesta
    audio = generar_audio(respuesta)
    with open(audio, "rb") as voz:
        await update.message.reply_voice(voice=voz)
    eliminar_audio(audio)

    # Enviar texto de la respuesta
    await update.message.reply_text(respuesta)

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

    # Analizar gráfica (educativo)
    mensaje_respuesta = (
        "✅ Imagen recibida. \n"
        "Analizando desde perspectiva educativa...\n"
        "Recuerda: esto es un ejemplo educativo, no una recomendación financiera."
    )

    # Enviar audio
    audio = generar_audio(mensaje_respuesta)
    with open(audio, "rb") as voz:
        await update.message.reply_voice(voice=voz)
    eliminar_audio(audio)

    # Enviar texto
    await update.message.reply_text(mensaje_respuesta)

    # Eliminar archivo temporal
    os.remove(path_local)

# =========================
# INICIALIZACIÓN DEL BOT
# =========================

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", panel_admin))

    # Panel admin botones
    app.add_handler(CallbackQueryHandler(ver_alumnos, pattern="admin_ver"))
    app.add_handler(CallbackQueryHandler(activar_alumno, pattern="admin_activar"))
    app.add_handler(CallbackQueryHandler(desactivar_alumno, pattern="admin_desactivar"))

    # Procesar ID enviado por admin
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_id_admin))

    # Mensajes alumnos (IA + audio)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensajes))

    # Imágenes (gráficas)
    app.add_handler(MessageHandler(filters.PHOTO, imagenes))

    # Ejecutar bot
    app.run_polling()

if __name__ == "__main__":
    main()
