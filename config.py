import os
from dotenv import load_dotenv

load_dotenv()

# Token del bot de Telegram
TOKEN = os.getenv("TELEGRAM_TOKEN")

# URI de MongoDB
MONGO_URI = os.getenv("MONGO_URI")

# Wallet del bot para recibir USDT BEP-20
USDT_WALLET = os.getenv("USDT_WALLET")
