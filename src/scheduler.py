# src/scheduler.py
import json
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from src import constants
from src.parser import Parser
from src.notifier import Notifier
from src.database import Database
import time
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат сообщений
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),  # Запись логов в файл
        logging.StreamHandler()  # Вывод логов в консоль
    ]
)
logger = logging.getLogger(__name__)
class Scheduler:
    def __init__(self, interval, bot):
        self.scheduler = BackgroundScheduler()
        self.db = Database()
        self.bot = bot
        self.notifier = Notifier()
        self.interval = interval

    def start(self):
        self.scheduler.add_job(self.check_new_ads, 'interval', seconds=self.interval)
        self.scheduler.start()

    #TODO: добавить гет по классу из бд
    #TODO: на стороне вотчера всю логшику сделать
    #TODO: чтобы не банило из-за запросов
    def check_new_ads(self):
        links = self.db.get_links()
        unique_links = set()
        if links is not None and len(links) > 0:
            unique_links = set(row for row in links)
        for link in unique_links:
            new_ads = self.check_new_ads_for_link(link)
            if new_ads is not None and len(new_ads) > 0:
                users = self.db.get_user_by_link(link.id)
                for user in users:
                    data = {
                        "user_id": user.user_id,
                        "new_ads": constants.Constant.delimeter.join(new_ads)  # Объединение с помощью разделителя
                    }
                    json_string = json.dumps(data)
                    self.bot.bot.send_message('7284602748', constants.Constant.SERVICE_COMMAND_PREFIX_OUTPUT + json_string)

    def check_new_ads_for_link(self, link):
        current_ads = Parser.parse_site(link.url)
        if current_ads is None:
            return []
        if current_ads is None:
            logging.info(f"Нет текущих объявлений для {link}.")
            return []
        current_ads = list(current_ads)
        current_ads = self.clean_links(current_ads)
        previous_ads = self.db.get_previous_adverts(link.id)
        new_ads = current_ads[:3]
        if previous_ads is None or len(previous_ads) == 0:
            # Если предыдущие объявления пустые, берем первые три текущих
            self.db.update_previous_adverts(link.id, new_ads)
            logging.info("Предыдущие объявления пустые. Добавлены новые: %s", new_ads)
            return new_ads
        else:
            new_ads = set(new_ads) - set(previous_ads)
            if new_ads:
                # Обновляем базу данных новыми объявлениями
                self.db.update_previous_adverts(link.id, new_ads)
                logging.info("Найдены новые объявления:", new_ads)
                return new_ads
            else:
                logging.info("Новых объявлений нет.")
                return None

    # Функция для удаления параметров rank_id и search_id
    def clean_links(self, links):
        cleaned_links = []
        for link in links:
            # Разделяем ссылку на базовую часть и параметры
            base_link = link.split('?')[0]
            params = link.split('?')[1:]  # Получаем параметры, если они есть

            if params:
                # Фильтруем параметры, исключая rank_id и search_id
                filtered_params = '&'.join(
                    param for param in params[0].split('&') if 'rank' not in param and 'searchId' not in param)
                # Если остались параметры, добавляем их к базовой части
                cleaned_link = base_link + ('?' + filtered_params if filtered_params else '')
            else:
                cleaned_link = base_link

            cleaned_links.append(cleaned_link)

        return cleaned_links

    def stop(self):
        self.scheduler.shutdown()
