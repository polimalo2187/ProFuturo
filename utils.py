from pymongo import MongoClient
from config import MONGO_URI

# Conexión a MongoDB
client = MongoClient(MONGO_URI)
db = client['trading_bot']

# Registrar usuario
def registrar_usuario(user_id, nombre):
    usuarios = db['usuarios']
    if not usuarios.find_one({"user_id": user_id}):
        usuarios.insert_one({
            "user_id": user_id,
            "nombre": nombre,
            "wallet": None,
            "estado_pago": False
        })
        return True
    return False

# Guardar wallet del usuario
def guardar_wallet(user_id, wallet):
    usuarios = db['usuarios']
    usuarios.update_one({"user_id": user_id}, {"$set": {"wallet": wallet}})

# Actualizar estado de pago
def actualizar_pago(user_id):
    usuarios = db['usuarios']
    usuarios.update_one({"user_id": user_id}, {"$set": {"estado_pago": True}})

# Obtener usuario por id
def obtener_usuario(user_id):
    usuarios = db['usuarios']
    return usuarios.find_one({"user_id": user_id})
