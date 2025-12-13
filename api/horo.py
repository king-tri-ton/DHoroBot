# coding: utf-8
from bs4 import BeautifulSoup
from .regular import remove_tags
import requests


ZODIAC_SIGNS = {
    'aries': '♈️ Овен',
    'taurus': '♉ Телец',
    'gemini': '♊ Близнецы',
    'cancer': '♋️ Рак',
    'leo': '♌ Лев',
    'virgo': '♍ Дева',
    'libra': '♎ Весы',
    'scorpio': '♏ Скорпион',
    'sagittarius': '♐ Стрелец',
    'capricorn': '♑ Козерог',
    'aquarius': '♒ Водолей',
    'pisces': '♓ Рыбы'
}


PERIOD_MAP = {
    'вчера': 'yesterday',
    'сегодня': 'today',
    'завтра': 'tomorrow',
    'неделя': 'week',
    'месяц': 'month',
    'год': 'year'
}


class HoroAPI:
    """
    Парсер гороскопов с сайта horo.mail.ru
    """

    BASE_URL = "https://horo.mail.ru/prediction/"

    def __init__(self, user_agent: str):
        """
        Инициализация парсера.

        Args:
            user_agent (str): User-Agent для HTTP-запросов. Обязателен.
        """
        if not user_agent:
            raise ValueError("User-Agent обязателен")
        self.user_agent = user_agent

    def fetch_page(self, url: str) -> tuple[str, str]:
        """
        Получает заголовок и текст гороскопа с указанной страницы.

        Args:
            url (str): Полная ссылка на страницу гороскопа.

        Returns:
            tuple[str, str]: Заголовок и текст гороскопа.
        """
        headers = {"User-Agent": self.user_agent}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find("h1", {"data-qa": "Title"})
        content_tag = soup.find("main", {"data-qa": "ArticleLayout"})
        if not title_tag or not content_tag:
            raise ValueError("Не удалось получить данные с сайта")
        title = title_tag.get_text(strip=True)
        content = remove_tags(str(content_tag))
        return title, content

    def get_today_all(self) -> tuple[str, str]:
        """
        Гороскоп на сегодня для всех знаков.

        Returns:
            tuple[str, str]: Заголовок и текст.
        """
        return self.fetch_page(self.BASE_URL)

    def get_horo(self, sign: str, date: str) -> tuple[str, str]:
        """
        Гороскоп для конкретного знака и даты.

        Args:
            sign (str): Знак зодиака (например, "aries").
            date (str): Дата (например, "today", "tomorrow").

        Returns:
            tuple[str, str]: Заголовок и текст.
        """
        url = f'{self.BASE_URL}{sign}/{date}/'
        return self.fetch_page(url)
