from bs4 import BeautifulSoup
from remove_tags import *
import requests
import re

# возвращает гороскоп для всех зз на сегодня
def getHoroTodayAll():
	headers = requests.utils.default_headers()
	headers.update({'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.0) AppleWebKit/532.1.0 (KHTML, like Gecko) Chrome/34.0.822.0 Safari/532.1.0',})
	url = requests.get('https://horo.mail.ru/prediction/', headers=headers)
	s = BeautifulSoup(url.text, 'html.parser')
	title = s.find("h1", {"class": "hdr__inner"}).getText()
	text = s.find("div", {"class": "article__item_alignment_left"}).getText()
	content = '<b>🗓 <a href="https://t.me/DHoroBot">'+title+'</a></b>\n\n💬 '+text
	return content

# возвращает указнный гороскоп
def getHoro(char, date):
	headers = requests.utils.default_headers()
	headers.update({'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.0) AppleWebKit/532.1.0 (KHTML, like Gecko) Chrome/34.0.822.0 Safari/532.1.0',})
	url = requests.get('https://horo.mail.ru/prediction/' + char + '/' + date + '/', headers=headers)
	s = BeautifulSoup(url.text, 'html.parser')
	title = s.find("h1", {"class": "hdr__inner"}).getText()
	date = s.find("span", {"class": "link__text"}).getText()
	text = s.find("div", {"class": "article__item_alignment_left"})
	text = re.sub(r'<a(.*?)</a>', '', str(text))
	text = remove_tags(text)
	content = '<b>☀️ <a href="https://t.me/DHoroBot">'+title+'</a></b>\n\n<b>🗓 '+date+'</b>\n\n💬 '+text
	return content

