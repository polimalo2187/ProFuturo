from pymongo import MongoClient
from config import MONGO_URI
from datetime import datetime

# Conexión a MongoDB
client = MongoClient(MONGO_URI)
db = client["profuturobot"]

# Colecciones
usuarios = db["usuarios"]
memoria = db["memoria"]

# =========================
# FUNCIONES DE USUARIOS
# =========================

def registrar_usuario(user_id, nombre, username):
    if not usuarios.find_one({"user_id": user_id}):
        usuarios.insert_one({
            "user_id": user_id,
            "nombre": nombre,
            "username": username,
            "activo": False,
            "fecha_registro": datetime.utcnow()
        })

def activar_usuario(user_id):
    usuarios.update_one(
        {"user_id": user_id},
        {"$set": {"activo": True}}
    )

def desactivar_usuario(user_id):
    usuarios.update_one(
        {"user_id": user_id},
        {"$set": {"activo": False}}
    )

def usuario_activo(user_id):
    usuario = usuarios.find_one({"user_id": user_id})
    return usuario and usuario.get("activo", False)

def obtener_usuarios():
    return list(usuarios.find())

# =========================
# MEMORIA DEL ALUMNO (IA)
# =========================

def obtener_memoria(user_id):
    doc = memoria.find_one({"user_id": user_id})
    if not doc:
        return {
            "perfil": "",
            "historial": []
        }
    return doc

def actualizar_memoria(user_id, perfil, historial):
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
