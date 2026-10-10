import os
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Takip edilecek Midas kripto referansları
WATCHED_COINS = ["BTCUSDT", "STRKUSDT", "LUMIAUSDT", "MAGICUSDT", "GALAUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT"]
