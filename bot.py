import asyncio
import json
import logging
import requests
from config import WATCHED_COINS
from signal_engine import SignalEngine

# Token ve Chat ID doğrudan gömülü
TELEGRAM_BOT_TOKEN = "8701079360:AAFzZZdPePGCdkOog1W7Ge8bZBAH0MV0zao"
TELEGRAM_CHAT_ID = "6073753368"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

engine = SignalEngine()

def send_telegram_alert(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            logger.info("Telegram bildirimi başarıyla gönderildi.")
            return True
        else:
            logger.error(f"Telegram API Hatası: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Telegram bağlantı istisnası: {e}")
        return False

async def monitor_market():
    send_telegram_alert("🟢 *Midas Kripto Radar* bulut üzerinde başarıyla başlatıldı ve piyasa takibine başladı!")
    logger.info("Piyasa veri döngüsü başlatılıyor...")

    while True:
        try:
            for coin in WATCHED_COINS:
                url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={coin}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    symbol = data.get("symbol")
                    price = float(data.get("lastPrice"))
                    volume = float(data.get("volume"))
                    
                    signal = engine.update_and_check(symbol, price, volume)
                    if signal:
                        msg = (
                            f"🚨 *KRİPTO RADAR — {signal['signal_type']}*\n\n"
                            f"🪙 *Coin:* `{signal['symbol']}`\n"
                            f"💵 *Fiyat:* `{signal['price']}`\n"
                            f"📊 *Değişim:* `% {signal['price_change']}` (Hacim: {signal['volume_ratio']}x)\n\n"
                            f"🔍 *Tespit:* {signal['reason']}\n"
                            f"⚠️ *Seviye:* {signal['level']}"
                        )
                        send_telegram_alert(msg)
                        logger.info(f"Sinyal Gönderildi ve Bildirim Atıldı: {symbol}")
                
                await asyncio.sleep(0.5)
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"Veri çekme hatası: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(monitor_market())
