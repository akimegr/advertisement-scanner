# src/parser.py
import requests
from bs4 import BeautifulSoup

class Parser:
    @staticmethod
    def parse_site(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Находим все <div> с указанным классом И БЕРЁМ КЛАСС 'styles_cards__bBppJ'
                # находим <div> где внутри section:
                # <div class = "styles_cards__bBppJ">
                # <section>....</section>
                # <section>....</section>
                # <section>....</section>
                # <section>....</section>
                # <section>....</section>
                #</div>
                div = soup.find('div', class_='styles_cards__HMGBx')
                if not div:
                    print("Div с заданным классом не найден.")
                    return []

                # Извлекаем все <section> внутри найденного <div>
                sections = div.find_all('section')

                # Список для хранения всех ссылок
                links = []

                # Ищем теги <a> внутри каждого <section>
                for section in sections:
                    a_tag = section.find('a', class_='styles_wrapper__Q06m9')
                    if a_tag and 'href' in a_tag.attrs:
                        links.append(a_tag['href'])

                return links
        except Exception as e:
            print(f"Ошибка при парсинге {url}: {e}")
            return []
