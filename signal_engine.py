import time
import numpy as np

class SignalEngine:
    def __init__(self):
        self.history = {}
        self.last_signal_time = {}

    def calculate_rsi(self, prices, period=14):
        if len(prices) < period + 1:
            return 50.0  # Yeterli veri yoksa nötr kabul et
        deltas = np.diff(prices)
        seed = deltas[:period]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        if down == 0:
            return 100.0
        rs = up / down
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return float(rsi)

    def update_and_check(self, symbol: str, price: float, volume: float, funding_rate: float = 0.0, open_interest_change: float = 0.0):
        current_time = time.time()
        
        if symbol not in self.history:
            self.history[symbol] = {"prices": [], "volumes": []}
            
        data = self.history[symbol]
        data["prices"].append(price)
        data["volumes"].append(volume)
        
        if len(data["prices"]) > 60:
            data["prices"].pop(0)
            data["volumes"].pop(0)
            
        if len(data["prices"]) < 15:
            return None

        prices = np.array(data["prices"])
        volumes = np.array(data["volumes"])
        
        # 1. RSI Hesaplama
        current_rsi = self.calculate_rsi(prices)

        # BTC Çöküş Koruma Filtresi
        if symbol != "BTCUSDT" and "BTCUSDT" in self.history:
            btc_prices = self.history["BTCUSDT"]["prices"]
            if len(btc_prices) >= 3:
                btc_drop = (btc_prices[-1] - btc_prices[-3]) / btc_prices[-3]
                if btc_drop < -0.015:
                    return {
                        "symbol": symbol, "price": price,
                        "signal_type": "RİSK UYARISI (BTC ÇÖKÜŞÜ)", "level": "SEVİYE 3",
                        "reason": f"Bitcoin'de ani düşüş tespit edildi (%{btc_drop*100:.2f}). Alım sinyalleri askıya alındı.",
                        "volume_ratio": 0.0, "price_change": round(btc_drop * 100, 2), "extra_info": f"RSI: {current_rsi:.1f}"
                    }

        if current_time - self.last_signal_time.get(symbol, 0) < 300:
            return None

        price_change_short = (prices[-1] - prices[-3]) / prices[-3]
        avg_volume = np.mean(volumes[:-1]) if len(volumes) > 1 else volumes[-1]
        volume_ratio = volumes[-1] / avg_volume if avg_volume > 0 else 1.0

        signal_type, level, reason = None, None, ""

        # 2. RSI Filtresi Kuralı: RSI 80 üzerindeyse (aşırı şişmişse) alım sinyali verme
        if current_rsi > 80:
            return None

        is_futures_confirmed = open_interest_change > 1.5 or (funding_rate > -0.001 and funding_rate < 0.005)

        if volume_ratio > 2.0 and price_change_short > 0.015 and is_futures_confirmed and (45 <= current_rsi <= 75):
            signal_type, level, reason = "DOĞRULANMIŞ FIRSAT (RSI & OI DESTEKLİ)", "SEVİYE 1", f"Hacim {volume_ratio:.1f}x patladı, RSI ({current_rsi:.1f}) sağlıklı yükseliş bölgesinde."
        elif volume_ratio > 3.0 and price_change_short > 0.035 and current_rsi < 78:
            signal_type, level, reason = "DOĞRULANMIŞ FIRSAT", "SEVİYE 1", f"Güçlü hacim patlaması ({volume_ratio:.1f}x) ve yukarı yönlü kırılım."
        elif volume_ratio > 2.0 and price_change_short > 0.015:
            signal_type, level, reason = "ERKEN UYARI", "SEVİYE 2", f"Normal hacmin {volume_ratio:.1f} katı hacim ve momentum artışı."

        if signal_type:
            self.last_signal_time[symbol] = current_time
            extra_text = f"📊 RSI: {current_rsi:.1f} | Fonlama: %{funding_rate*100:.4f}"
            return {
                "symbol": symbol, "price": price, "signal_type": signal_type,
                "level": level, "reason": reason, "volume_ratio": round(volume_ratio, 2),
                "price_change": round(price_change_short * 100, 2), "extra_info": extra_text
            }
        return None
