# src/notifier.py
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN

class Notifier:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)

    def notify_user(self, user_id, ads):
        message = f"Новые объявления:\n" + "\n".join(ads)
        self.bot.send_message(chat_id=user_id, text=message)
