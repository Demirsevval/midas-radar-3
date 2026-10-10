import time
import numpy as np

class SignalEngine:
    def __init__(self):
        self.history = {}
        self.last_signal_time = {}

    def update_and_check(self, symbol: str, price: float, volume: float, funding_rate: float = 0.0, open_interest_change: float = 0.0):
        current_time = time.time()
        
        if symbol not in self.history:
            self.history[symbol] = {"prices": [], "volumes": []}
            
        data = self.history[symbol]
        data["prices"].append(price)
        data["volumes"].append(volume)
        
        if len(data["prices"]) > 50:
            data["prices"].pop(0)
            data["volumes"].pop(0)
            
        if len(data["prices"]) < 10:
            return None

        prices = np.array(data["prices"])
        volumes = np.array(data["volumes"])
        
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
                        "volume_ratio": 0.0, "price_change": round(btc_drop * 100, 2), "extra_info": ""
                    }

        if current_time - self.last_signal_time.get(symbol, 0) < 300:
            return None

        price_change_short = (prices[-1] - prices[-3]) / prices[-3]
        avg_volume = np.mean(volumes[:-1]) if len(volumes) > 1 else volumes[-1]
        volume_ratio = volumes[-1] / avg_volume if avg_volume > 0 else 1.0

        signal_type, level, reason = None, None, ""

        # Gelişmiş Filtre: Hacim patlaması + Türev piyasa (OI artışı veya makul fonlama oranı) teyidi
        is_futures_confirmed = open_interest_change > 1.5 or (funding_rate > -0.001 and funding_rate < 0.005)

        if volume_ratio > 2.0 and price_change_short > 0.015 and is_futures_confirmed:
            signal_type, level, reason = "DOĞRULANMIŞ FIRSAT (OI DESTEKLİ)", "SEVİYE 1", f"Hacim {volume_ratio:.1f}x arttı, açık pozisyonlar ve momentum pozitif."
        elif volume_ratio > 3.0 and price_change_short > 0.035:
            signal_type, level, reason = "DOĞRULANMIŞ FIRSAT", "SEVİYE 1", f"Güçlü hacim patlaması ({volume_ratio:.1f}x) ve yukarı yönlü kırılım."
        elif volume_ratio > 2.0 and price_change_short > 0.015:
            signal_type, level, reason = "ERKEN UYARI", "SEVİYE 2", f"Normal hacmin {volume_ratio:.1f} katı hacim ve momentum artışı."

        if signal_type:
            self.last_signal_time[symbol] = current_time
            extra_text = f"📈 Fonlama: %{funding_rate*100:.4f} | OI Değişim: %{open_interest_change:.1f}"
            return {
                "symbol": symbol, "price": price, "signal_type": signal_type,
                "level": level, "reason": reason, "volume_ratio": round(volume_ratio, 2),
                "price_change": round(price_change_short * 100, 2), "extra_info": extra_text
            }
        return None
