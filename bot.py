import asyncio
import json
import logging
import requests
from config import WATCHED_COINS
from signal_engine import SignalEngine

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
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Telegram hata: {e}")
        return False

async def monitor_market():
    send_telegram_alert("🟢 *Midas Kripto Radar v3* (RSI ve Fonlama Filtreli) başarıyla başlatıldı!")
    logger.info("Piyasa veri döngüsü başlatılıyor...")

    while True:
        try:
            for coin in WATCHED_COINS:
                ticker_url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={coin}"
                res = requests.get(ticker_url, timeout=5)
                
                if res.status_code == 200:
                    data = res.json()
                    symbol = data.get("symbol")
                    price = float(data.get("lastPrice"))
                    volume = float(data.get("volume"))
                    
                    funding_rate = 0.0
                    try:
                        f_url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"
                        f_res = requests.get(f_url, timeout=3)
                        if f_res.status_code == 200:
                            funding_rate = float(f_res.json().get("lastFundingRate", 0.0))
                    except:
                        pass

                    oi_change = 0.0
                    try:
                        oi_url = f"https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol}"
                        oi_res = requests.get(oi_url, timeout=3)
                        if oi_res.status_code == 200:
                            oi_change = 2.0 
                    except:
                        pass

                    signal = engine.update_and_check(symbol, price, volume, funding_rate, oi_change)
                    
                    if signal:
                        extra_line = f"\n{signal.get('extra_info', '')}" if signal.get('extra_info') else ""
                        msg = (
                            f"🚨 *KRİPTO RADAR — {signal['signal_type']}*\n\n"
                            f"🪙 *Coin:* `{signal['symbol']}`\n"
                            f"💵 *Fiyat:* `{signal['price']}`\n"
                            f"📊 *Değişim:* `% {signal['price_change']}` (Hacim: {signal['volume_ratio']}x)"
                            f"{extra_line}\n\n"
                            f"🔍 *Tespit:* {signal['reason']}\n"
                            f"⚠️ *Seviye:* {signal['level']}"
                        )
                        send_telegram_alert(msg)
                        logger.info(f"Sinyal Gönderildi: {symbol}")
                
                await asyncio.sleep(0.5)
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"Veri döngüsü hatası: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(monitor_market())
                    data = res.json()
                    symbol = data.get("symbol")
                    price = float(data.get("lastPrice"))
                    volume = float(data.get("volume"))
                    
                    funding_rate = 0.0
                    try:
                        f_url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"
                        f_res = requests.get(f_url, timeout=3)
                        if f_res.status_code == 200:
                            funding_rate = float(f_res.json().get("lastFundingRate", 0.0))
                    except:
                        pass

                    oi_change = 0.0
                    try:
                        oi_url = f"https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol}"
                        oi_res = requests.get(oi_url, timeout=3)
                        if oi_res.status_code == 200:
                            oi_change = 2.0 
                    except:
                        pass

                    signal = engine.update_and_check(symbol, price, volume, funding_rate, oi_change)
                    
                    if signal:
                        extra_line = f"\n{signal.get('extra_info', '')}" if signal.get('extra_info') else ""
                        msg = (
                            f"🚨 *KRİPTO RADAR — {signal['signal_type']}*\n\n"
                            f"🪙 *Coin:* `{signal['symbol']}`\n"
                            f"💵 *Fiyat:* `{signal['price']}`\n"
                            f"📊 *Değişim:* `% {signal['price_change']}` (Hacim: {signal['volume_ratio']}x)"
                            f"{extra_line}\n\n"
                            f"🔍 *Tespit:* {signal['reason']}\n"
                            f"⚠️ *Seviye:* {signal['level']}"
                        )
                        send_telegram_alert(msg)
                        logger.info(f"RSI Filtreli Sinyal Gönderildi: {symbol}")
                
                await asyncio.sleep(0.5)
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"Veri döngüsü hatası: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(monitor_market())
                if res.status_code == 200:
                    data = res.json()
                    symbol = data.get("symbol")
                    price = float(data.get("lastPrice"))
                    volume = float(data.get("volume"))
                    
                    # 2. Vadeli taraf (Fonlama Oranı) verisi çekme
                    funding_rate = 0.0
                    try:
                        f_url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"
                        f_res = requests.get(f_url, timeout=3)
                        if f_res.status_code == 200:
                            funding_rate = float(f_res.json().get("lastFundingRate", 0.0))
                    except:
                        pass

                    # 3. Açık Pozisyon (Open Interest) verisi çekme
                    oi_change = 0.0
                    try:
                        oi_url = f"https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol}"
                        oi_res = requests.get(oi_url, timeout=3)
                        if oi_res.status_code == 200:
                            # Basit bir simülasyon/değişim referansı
                            oi_change = 2.0 
                    except:
                        pass

                    # Sinyal motoruna verileri gönder
                    signal = engine.update_and_check(symbol, price, volume, funding_rate, oi_change)
                    
                    if signal:
                        extra_line = f"\n{signal.get('extra_info', '')}" if signal.get('extra_info') else ""
                        msg = (
                            f"🚨 *KRİPTO RADAR — {signal['signal_type']}*\n\n"
                            f"🪙 *Coin:* `{signal['symbol']}`\n"
                            f"💵 *Fiyat:* `{signal['price']}`\n"
                            f"📊 *Değişim:* `% {signal['price_change']}` (Hacim: {signal['volume_ratio']}x)"
                            f"{extra_line}\n\n"
                            f"🔍 *Tespit:* {signal['reason']}\n"
                            f"⚠️ *Seviye:* {signal['level']}"
                        )
                        send_telegram_alert(msg)
                        logger.info(f"Gelişmiş Sinyal Gönderildi: {symbol}")
                
                await asyncio.sleep(0.5)
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"Veri döngüsü hatası: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(monitor_market())
