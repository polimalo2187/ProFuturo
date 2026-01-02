from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from config import TELEGRAM_TOKEN
from database import usuarios
from ai_engine import responder
from admin_panel import (
    panel_admin,
    ver_alumnos,
    activar_alumno,
    desactivar_alumno,
    procesar_id
)

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    usuario = usuarios.find_one({"user_id": user.id})

    if not usuario or not usuario.get("activo"):
        await update.message.reply_text(
            "🚫 No formas parte de la academia actualmente.\n"
            "Contacta con tu profesor."
        )
        return

    await update.message.reply_text(
        "🎓 Bienvenido.\n"
        "Soy tu asesor personal de trading 24/7.\n"
        "Puedes preguntarme cualquier duda."
    )

# Mensajes de alumnos activos
async def mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    usuario = usuarios.find_one({"user_id": user_id})

    if not usuario or not usuario.get("activo"):
        await update.message.reply_text("🚫 Acceso no activo.")
        return

    respuesta = responder(update.message.text)
    await update.message.reply_text(respuesta)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", panel_admin))

    app.add_handler(CallbackQueryHandler(ver_alumnos, pattern="ver_alumnos"))
    app.add_handler(CallbackQueryHandler(activar_alumno, pattern="activar_alumno"))
    app.add_handler(CallbackQueryHandler(desactivar_alumno, pattern="desactivar_alumno"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_id))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensajes))

    app.run_polling()

if __name__ == "__main__":
    main()
