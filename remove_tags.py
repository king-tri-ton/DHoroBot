import re

def remove_tags(text):
	return re.compile(r'<[^>]+>').sub('', text)