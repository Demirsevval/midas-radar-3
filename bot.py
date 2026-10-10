import asyncio
import json
import logging
import requests
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
    send_telegram_alert("🟢 *Midas Kripto Radar v5* (Tüm Piyasa / Sınırsız Tarama) başarıyla başlatıldı!")
    logger.info("Binance üzerindeki tüm USDT pariteleri otomatik taranıyor...")

    while True:
        try:
            # Binance üzerindeki tüm coinlerin 24 saatlik verisini tek seferde çek
            url = "https://api.binance.com/api/v3/ticker/24hr"
            res = requests.get(url, timeout=10)
            
            if res.status_code == 200:
                tickers = res.json()
                
                for ticker in tickers:
                    symbol = ticker.get("symbol")
                    
                    # Sadece USDT paritelerini al, stablecoinleri (USDC vb.) dışarıda bırak
                    if symbol.endswith("USDT") and symbol not in ["USDCUSDT", "USDTUSDT", "FDUSDUSDT", "TUSDUSDT", "EURUSDT"]:
                        try:
                            price = float(ticker.get("lastPrice"))
                            volume = float(ticker.get("volume"))
                            
                            # Hızlı ön eleme: İşlem hacmi çok düşük olan ölü coinleri atla (performans için)
                            if volume < 50000:
                                continue

                            # Vadeli fonlama oranını hızlıca kontrol et
                            funding_rate = 0.0
                            try:
                                f_url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"
                                f_res = requests.get(f_url, timeout=1)
                                if f_res.status_code == 200:
                                    funding_rate = float(f_res.json().get("lastFundingRate", 0.0))
                            except:
                                pass

                            oi_change = 2.0 

                            # Sinyal motoruna gönder
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
                                logger.info(f"Sinyal Yakalandı ve Gönderildi: {symbol}")
                        except Exception:
                            continue
                            
            # Tüm piyasa tarandıktan sonra döngü arasında 10 saniye bekle
            await asyncio.sleep(10)
            
        except Exception as e:
            logger.error(f"Genel piyasa döngü hatası: {e}")
            await asyncio.sleep(15)

if __name__ == "__main__":
    asyncio.run(monitor_market())
