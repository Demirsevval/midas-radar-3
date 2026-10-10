import asyncio
import json
import logging
import requests
import websockets
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, WATCHED_COINS
from signal_engine import SignalEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

engine = SignalEngine()

def send_telegram_alert(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Token veya Chat ID eksik!")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Telegram hata: {e}")
        return False

async def monitor_market():
    # Bot başlarken test mesajı gönder
    send_telegram_alert("🟢 *Midas Kripto Radar* sıfırdan kurulum ile başarıyla başlatıldı ve BTC korumalı takibe başladı!")
    
    streams = "/".join([f"{coin.lower()}@ticker" for coin in WATCHED_COINS])
    url = f"wss://stream.binance.com:9443/stream?streams={streams}"
    
    while True:
        try:
            async with websockets.connect(url) as websocket:
                logger.info("WebSocket bağlantısı aktif.")
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if "data" in data:
                        ticker = data["data"]
                        signal = engine.update_and_check(ticker.get("s"), float(ticker.get("c")), float(ticker.get("v")))
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
        except Exception as e:
                            logger.error(f"Bağlantı hatası: {e}")
                            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(monitor_market())
