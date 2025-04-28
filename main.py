 
import os
from flask import Flask

app = Flask(__name__)
import requests
import time
import os

TELEGRAM_TOKEN = "7660306321:AAEzucY4lkSY3KPhKrSE1AP75hYQDyshHAk"
CHAT_ID = "5257769460"
THRESHOLD = 10.0

def get_usdt_pairs():
    url = "https://api.binance.com/api/v3/ticker/price"
    data = requests.get(url).json()
    if isinstance(data, list):
        return [item['symbol'] for item in data if isinstance(item, dict) and item.get('symbol', '').endswith('USDT')]
    return []

def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        data = requests.get(url, timeout=5).json()
        return float(data['price'])
    except:
        return None

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=payload)

def monitor():
    print("Бот запущен. Сканируем рынок...")
    tracked_prices = {}

    while True:
        pairs = get_usdt_pairs()
        for symbol in pairs:
            price = get_price(symbol)
            if price is None:
                continue

            if symbol not in tracked_prices:
                tracked_prices[symbol] = (price, time.time())
            else:
                old_price, timestamp = tracked_prices[symbol]
                if time.time() - timestamp >= 300:
                    change = ((price - old_price) / old_price) * 100
                    if abs(change) >= THRESHOLD:
                        direction = "ПАМП" if change > 0 else "ДАМП"
                        send_telegram_message(
                            f"{direction} на {symbol}: {change:.2f}% за 5 минут\nЦена: {price} USDT"
                        )
                    tracked_prices[symbol] = (price, time.time())
        time.sleep(60)
     
@app.route('/')
def home():
    return 'Crypto Monitor Bot is running!'

monitor()
 
 if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render передаёт PORT через переменную окружения
    app.run(host='0.0.0.0', port=port)
