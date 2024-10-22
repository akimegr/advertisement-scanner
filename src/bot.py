import telebot
import json
from config import TELEGRAM_BOT_TOKEN
from src.database import Database
from src.constants import Constant

class Bot:


    def __init__(self):
        self.db = Database()
        self.bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

        @self.bot.message_handler(commands=["start"])
        def start_message_command(message):
            user_id = message.from_user.id
            try:
                self.bot.send_message(user_id, "Привет! Это служебный бот. Пишите основному боту https://t.me/ChannelsScannerBot !")
            except Exception as e:
                self.bot.send_message(user_id, "Произошла ошибка. Пожалуйста, попробуйте позже.")

        @self.bot.message_handler(func=lambda message: message.text.startswith(Constant.SERVICE_COMMAND_PREFIX_INPUT))
        def handle_incoming_message(message):
            user_id = message.from_user.id
            try:
                # Предполагаем, что сообщение содержит JSON-данные
                data = json.loads(message.text[len(Constant.SERVICE_COMMAND_PREFIX_INPUT):].strip())

                # Проверяем наличие ключей user_id и url
                if "user_id" in data and "url" in data:
                    user_id_bd = data["user_id"]
                    url = data["url"]
                    self.process_url(user_id_bd, url)
                    self.bot.send_message(user_id, f"URL {url} успешно добавлен в базу данных.")
                else:
                    self.bot.send_message(message.chat.id, "Некорректные данные. Ожидались ключи 'user_id' и 'url'.")
            except json.JSONDecodeError:
                self.bot.send_message(message.chat.id, "Ошибка в формате сообщения. Ожидался JSON.")
            except Exception as e:
                self.bot.send_message(message.chat.id, "Произошла ошибка при обработке сообщения.")


        @self.bot.message_handler(func=lambda message: (not(message.text.startswith(Constant.SERVICE_COMMAND_PREFIX_INPUT))))
        def handle_incoming_message(message):
            user_id = message.from_user.id
            try:
                self.bot.send_message(user_id, "Привет! Это служебный бот. Пишите основному боту https://t.me/ChannelsScannerBot !")
            except json.JSONDecodeError:
                self.bot.send_message(message.chat.id, "Ошибка в формате сообщения. Ожидался JSON.")
            except Exception as e:
                self.bot.send_message(message.chat.id, "Произошла ошибка при обработке сообщения.")

    def process_url(self, user_id, url):
        # Логика обработки URL и сохранения в базе данных
        self.db.add_link(user_id, url)

    def update_sort_parameter(self, link):
        # Разделяем ссылку на базовую часть и параметры
        base_link = link.split('?')[0]
        params = link.split('?')[1:]  # Получаем параметры, если они есть

        if params:
            # Разделяем параметры на отдельные элементы
            param_list = params[0].split('&')
            # Проверяем, есть ли параметр sort
            for i, param in enumerate(param_list):
                if param.startswith('sort='):
                    # Заменяем значение параметра sort
                    param_list[i] = 'sort=lst.d'
                    break
            else:
                # Если параметра sort не было, добавляем его
                param_list.append('sort=lst.d')

            # Собираем параметры обратно в строку
            updated_params = '&'.join(param_list)
            updated_link = base_link + '?' + updated_params
        else:
            # Если параметров нет, просто добавляем sort=lst.d
            updated_link = base_link + '?sort=lst.d'

        return updated_link

    def is_admin(self, user_id):
        user = self.db_ps_manager.get_user_by_id(user_id)
        return user is not None and Constant.Role.ADMIN == user.role

    def run(self):
        self.bot.polling(none_stop=True)

if __name__ == "__main__":
    bot = Bot()
    bot.run()
