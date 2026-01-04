import os
import logging
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
# CONFIGURAR LOGGING
# =========================
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =========================
# COMANDOS INICIALES
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"Comando /start recibido de {user.id} - {user.username}")

    registrar_usuario(user.id, user.first_name, user.username or "")

    if not usuario_activo(user.id):
        await update.message.reply_text(
            "🚫 No formas parte de la academia actualmente.\n"
            "Contacta con tu profesor para activarte."
        )
        logger.info(f"Usuario {user.id} NO activo. /start detenido.")
        return

    if es_primera_vez(user.id):
        mensaje_bienvenida = (
            "Bienvenido a Crono Assistant. "
            "Soy tu asesor personal de trading disponible 24/7. "
            "Puedo ayudarte a entender gráficos, conceptos y escenarios de trading. "
            "Recuerda: esto es contenido educativo y no asesoría financiera."
        )

        audio = generar_audio(mensaje_bienvenida)
        with open(audio, "rb") as voz:
            await update.message.reply_voice(voice=voz)
        await update.message.reply_text(mensaje_bienvenida)
        eliminar_audio(audio)
        marcar_bienvenida_enviada(user.id)
        logger.info(f"Bienvenida enviada a {user.id}")

# =========================
# MENSAJES DE ALUMNOS
# =========================

async def mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    logger.info(f"Mensaje recibido de {user_id} (@{username}): {update.message.text}")

    if user_id == ADMIN_ID:
        logger.info("Mensaje del admin ignorado en handler de alumnos.")
        return

    if not usuario_activo(user_id):
        await update.message.reply_text("🚫 Acceso no activo.")
        logger.info(f"Usuario {user_id} no activo. Mensaje no procesado.")
        return

    if update.message.text:
        texto_usuario = update.message.text
        try:
            respuesta = responder(user_id, texto_usuario)
            logger.info(f"Respuesta generada para {user_id}: {respuesta}")

            audio = generar_audio(respuesta)
            with open(audio, "rb") as voz:
                await update.message.reply_voice(voice=voz)
            eliminar_audio(audio)
            await update.message.reply_text(respuesta)
        except Exception as e:
            logger.error(f"Error generando respuesta para {user_id}: {e}")
            await update.message.reply_text("⚠️ Ocurrió un error al procesar tu mensaje.")

# =========================
# MENSAJES DE ADMIN
# =========================

async def mensajes_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        logger.warning(f"Usuario {user_id} intentó usar comandos de admin.")
        return

    logger.info(f"Mensaje de admin recibido: {update.message.text}")
    await procesar_id_admin(update, context)

# =========================
# MENSAJES DE IMÁGENES
# =========================

async def imagenes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    logger.info(f"Imagen recibida de {user_id}")

    if not usuario_activo(user_id):
        await update.message.reply_text("🚫 Acceso no activo.")
        logger.info(f"Usuario {user_id} no activo. Imagen no procesada.")
        return

    try:
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
        logger.info(f"Imagen procesada para {user_id}")
    except Exception as e:
        logger.error(f"Error procesando imagen de {user_id}: {e}")
        await update.message.reply_text("⚠️ Ocurrió un error al procesar la imagen.")

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

    # Mensajes admin (solo ADMIN_ID)
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID),
        mensajes_admin
    ))

    # Mensajes alumnos (todos los demás usuarios activos)
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        mensajes
    ))

    # Mensajes con imágenes
    app.add_handler(MessageHandler(filters.PHOTO, imagenes))

    logger.info("Bot iniciado y listo para recibir mensajes...")
    app.run_polling()

if __name__ == "__main__":
    main()
