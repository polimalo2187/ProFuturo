import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

# TU Telegram ID (ADMIN)
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
