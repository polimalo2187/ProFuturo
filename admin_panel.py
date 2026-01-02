from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from config import ADMIN_ID
from database import usuarios

# Verifica si es admin
def es_admin(user_id):
    return user_id == ADMIN_ID

# Panel principal
async def panel_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update.effective_user.id):
        return

    keyboard = [
        [InlineKeyboardButton("➕ Activar alumno", callback_data="activar_alumno")],
        [InlineKeyboardButton("📋 Ver alumnos", callback_data="ver_alumnos")],
        [InlineKeyboardButton("➖ Desactivar alumno", callback_data="desactivar_alumno")]
    ]

    await update.message.reply_text(
        "👑 Panel de administrador",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Mostrar alumnos
async def ver_alumnos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lista = usuarios.find()
    mensaje = "📋 Alumnos registrados:\n\n"

    for u in lista:
        mensaje += (
            f"👤 {u.get('nombre')}\n"
            f"Usuario: @{u.get('username', 'N/A')}\n"
            f"ID: {u.get('user_id')}\n"
            f"Estado: {'ACTIVO' if u.get('activo') else 'INACTIVO'}\n\n"
        )

    await query.message.reply_text(mensaje or "No hay alumnos registrados.")

# Activar alumno
async def activar_alumno(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["accion"] = "activar"
    await query.message.reply_text("📨 Envíame el Telegram ID del alumno a ACTIVAR")

# Desactivar alumno
async def desactivar_alumno(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["accion"] = "desactivar"
    await query.message.reply_text("📨 Envíame el Telegram ID del alumno a DESACTIVAR")

# Procesar ID enviado
async def procesar_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update.effective_user.id):
        return

    if "accion" not in context.user_data:
        return

    try:
        user_id = int(update.message.text)
    except ValueError:
        await update.message.reply_text("❌ ID inválido")
        return

    if context.user_data["accion"] == "activar":
        usuarios.update_one(
            {"user_id": user_id},
            {"$set": {"activo": True}},
            upsert=True
        )
        await update.message.reply_text("✅ Alumno activado")

    elif context.user_data["accion"] == "desactivar":
        usuarios.update_one(
            {"user_id": user_id},
            {"$set": {"activo": False}}
        )
        await update.message.reply_text("⛔ Alumno desactivado")

    context.user_data.clear()
