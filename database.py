from pymongo import MongoClient
from config import MONGO_URI
from datetime import datetime

# =========================
# CONEXIÓN A MONGO
# =========================
client = MongoClient(MONGO_URI)
db = client["profuturobot"]

# Colecciones
usuarios = db["usuarios"]
memoria = db["memoria"]

# =========================
# FUNCIONES DE USUARIOS
# =========================

def registrar_usuario(user_id, nombre, username):
    """
    Registra un usuario si no existe.
    Devuelve True si es la primera vez que se registra.
    """
    if not usuarios.find_one({"user_id": user_id}):
        usuarios.insert_one({
            "user_id": user_id,
            "nombre": nombre,
            "username": username,
            "activo": False,
            "bienvenida_enviada": False,  # Para controlar mensaje de bienvenida
            "fecha_registro": datetime.utcnow()
        })
        return True
    return False

def activar_usuario(user_id):
    """
    Activa a un usuario existente.
    """
    usuarios.update_one(
        {"user_id": user_id},
        {"$set": {"activo": True}}
    )

def desactivar_usuario(user_id):
    """
    Desactiva a un usuario existente.
    """
    usuarios.update_one(
        {"user_id": user_id},
        {"$set": {"activo": False}}
    )

def usuario_activo(user_id):
    """
    Devuelve True si el usuario está activo.
    """
    usuario = usuarios.find_one({"user_id": user_id})
    return usuario and usuario.get("activo", False)

def obtener_usuarios():
    """
    Retorna la lista de todos los usuarios.
    """
    return list(usuarios.find())

# =========================
# CONTROL DE BIENVENIDA
# =========================

def es_primera_vez(user_id):
    """
    Devuelve True si es la primera vez que el usuario entra al bot (no recibió bienvenida).
    """
    usuario = usuarios.find_one({"user_id": user_id})
    if usuario:
        return not usuario.get("bienvenida_enviada", False)
    return True

def marcar_bienvenida_enviada(user_id):
    """
    Marca que el usuario ya recibió el mensaje de bienvenida.
    """
    usuarios.update_one(
        {"user_id": user_id},
        {"$set": {"bienvenida_enviada": True}}
    )

# =========================
# MEMORIA DEL ALUMNO (IA)
# =========================

def obtener_memoria(user_id):
    """
    Obtiene la memoria del alumno para la IA.
    """
    doc = memoria.find_one({"user_id": user_id})
    if not doc:
        return {
            "perfil": "",
            "historial": []
        }
    return doc

def actualizar_memoria(user_id, perfil, historial):
    """
    Actualiza o crea la memoria del alumno para la IA.
    """
    memoria.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "perfil": perfil,
                "historial": historial,
                "actualizado": datetime.utcnow()
            }
        },
        upsert=True
  )
