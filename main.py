# main.py
import asyncio
import logging

from config import POLLING_INTERVAL
from src.bot import Bot
from src.scheduler import Scheduler

logging.basicConfig(
    level=logging.INFO,  # Уровень логирования: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат сообщений
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),  # Запись логов в файл
        logging.StreamHandler()  # Вывод логов в консоль
    ]
)
logger = logging.getLogger(__name__)
async def main():

    bot = Bot()

    print("Бот запущен")

    try:
        scheduler = Scheduler(POLLING_INTERVAL, bot)
        scheduler.start()
        await asyncio.gather(
            asyncio.to_thread(bot.bot.polling, none_stop=True, interval=0)  # Запуск polling в отдельном потоке
        )
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        bot.bot.stop_polling()  # Остановка polling бота

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped manually")
