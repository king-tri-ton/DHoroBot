import re

def remove_tags(text):
	return re.compile(r'<[^>]+>').sub('', text)

def is_valid_birthdate(date):
	"""
	Проверяет формат даты рождения:
	ДЕНЬ.МЕСЯЦ.ГОД без ведущих нулей.
	Примеры валидных: 3.5.1999, 5.12.1998
	"""
	pattern = r'^(?:[1-9]|[12][0-9]|3[01])\.(?:[1-9]|1[0-2])\.[0-9]{4}$'
	return bool(re.match(pattern, date.strip()))
