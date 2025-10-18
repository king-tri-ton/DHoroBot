from bs4 import BeautifulSoup
from regular import remove_tags
import requests
import re


def fetch_horo_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.0) AppleWebKit/532.1.0 (KHTML, like Gecko) Chrome/34.0.822.0 Safari/532.1.0',
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find("h1", {"data-qa": "Title"}).get_text()
    content = soup.find("main", {"data-qa": "ArticleLayout"})
    content = re.sub(r'<a(.*?)</a>', '', str(content))
    content = remove_tags(content)
    return title, content


def getHoroTodayAll():
    url = 'https://horo.mail.ru/prediction/'
    title, text = fetch_horo_page(url)
    content = f'<b>🗓 <a href="https://t.me/DHoroBot">{title}</a></b>\n\n💬 {text}'
    return content


def getHoro(char, date):
    url = f'https://horo.mail.ru/prediction/{char}/{date}/'
    title, text = fetch_horo_page(url)
    content = f'<b>☀️ <a href="https://t.me/DHoroBot">{title}</a></b>\n\n💬 {text}'
    return content
