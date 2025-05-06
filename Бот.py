import requests
import time
import logging
from telegram import Bot
import asyncio

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = "8007348023:AAGnhP0205aNZaXzX_cHrUyUdLmqlWCBako"
CHAT_ID = "473293195"
PRICE_JUMP_THRESHOLD = 0.0001  # минимальный порог изменения (в процентах)
CHECK_INTERVAL = 60  # секунд

bot = Bot(token=TELEGRAM_TOKEN)
logging.basicConfig(level=logging.INFO)

def get_futures_pairs():
    try:
        res = requests.get("https://contract.mexc.com/api/v1/contract/detail")
        data = res.json().get('data', [])
        symbols = [item['symbol'] for item in data]
        return symbols
    except Exception as e:
        logging.error(f"Ошибка получения списка контрактов: {e}")
        return []

def get_price(symbol):
    try:
        url = f"https://contract.mexc.com/api/v1/contract/realTime?symbol={symbol}"
        res = requests.get(url)
        price = float(res.json()['data']['lastPrice'])
        return price
    except Exception as e:
        logging.warning(f"Ошибка получения цены {symbol}: {e}")
        return None

async def main():
    last_prices = {}
    await bot.send_message(chat_id=CHAT_ID, text="🤖 Бот запущен и следит за рынком")
    logging.info("Бот запущен ✅")

    while True:
        symbols = get_futures_pairs()
        if not symbols:
            logging.error("Контракты не найдены. Бот завершает работу.")
            return

        for symbol in symbols:
            current_price = get_price(symbol)
            if current_price is None:
                continue

            if symbol in last_prices:
                old_price = last_prices[symbol]
                change = ((current_price - old_price) / old_price) * 100

                if abs(change) >= PRICE_JUMP_THRESHOLD:
                    direction = "⬆️" if change > 0 else "⬇️"
                    message = f"{direction} {symbol}: {change:.4f}% за {CHECK_INTERVAL} сек\nЦена: {current_price:.6f}"
                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=message)
                        logging.info(f"Сигнал: {message}")
                    except Exception as e:
                        logging.error(f"Ошибка при отправке сообщения: {e}")

            last_prices[symbol] = current_price

        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())