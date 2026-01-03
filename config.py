import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# MongoDB
MONGO_URI = os.getenv("MONGO_URI")

# Administrador (TU Telegram ID)
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configuración general del bot
BOT_NAME = "ProFuturoBot"
LANGUAGE = "es"

# Memoria del alumno
# Número máximo de mensajes recientes usados + perfil permanente resumido
MAX_CONTEXT_MESSAGES = 10
