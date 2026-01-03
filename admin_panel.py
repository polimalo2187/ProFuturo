from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from config import ADMIN_ID
from database import (
    registrar_usuario,
    activar_usuario,
    desactivar_usuario,
    obtener_usuarios
)

# =========================
# VERIFICACIÓN ADMIN
# =========================

def es_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

# =========================
# PANEL PRINCIPAL
# =========================

async def panel_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update.effective_user.id):
        return

    keyboard = [
        [InlineKeyboardButton("➕ Activar alumno", callback_data="admin_activar")],
        [InlineKeyboardButton("➖ Desactivar alumno", callback_data="admin_desactivar")],
        [InlineKeyboardButton("📋 Ver alumnos", callback_data="admin_ver")]
    ]

    await update.message.reply_text(
        "👑 Panel de control del administrador",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# VER ALUMNOS
# =========================

async def ver_alumnos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    alumnos = obtener_usuarios()
    if not alumnos:
        await query.message.reply_text("No hay alumnos registrados.")
        return

    mensaje = "📋 Alumnos registrados:\n\n"
    for a in alumnos:
        mensaje += (
            f"👤 {a.get('nombre')}\n"
            f"Usuario: @{a.get('username', 'N/A')}\n"
            f"ID: {a.get('user_id')}\n"
            f"Estado: {'ACTIVO' if a.get('activo') else 'INACTIVO'}\n"
            "-------------------------\n"
        )

    await query.message.reply_text(mensaje)

# =========================
# ACTIVAR / DESACTIVAR
# =========================

async def activar_alumno(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["accion_admin"] = "activar"
    await query.message.reply_text("📨 Envíame el Telegram ID del alumno a ACTIVAR")

async def desactivar_alumno(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["accion_admin"] = "desactivar"
    await query.message.reply_text("📨 Envíame el Telegram ID del alumno a DESACTIVAR")

# =========================
# PROCESAR ID ENVIADO
# =========================

async def procesar_id_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update.effective_user.id):
        return

    accion = context.user_data.get("accion_admin")
    if not accion:
        return

    try:
        user_id = int(update.message.text)
    except ValueError:
        await update.message.reply_text("❌ ID inválido.")
        return

    if accion == "activar":
        activar_usuario(user_id)
        await update.message.reply_text("✅ Alumno ACTIVADO correctamente.")

    elif accion == "desactivar":
        desactivar_usuario(user_id)
        await update.message.reply_text("⛔ Alumno DESACTIVADO correctamente.")

    context.user_data.clear()
