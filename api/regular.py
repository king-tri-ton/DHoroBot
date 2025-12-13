# coding: utf-8
import re

def remove_tags(text: str) -> str:
    """
    Убирает все HTML-теги из текста, обеспечивая правильные переносы строк.
    """
    
    # 1. Заменяем ЗАКРЫВАЮЩИЕ блочные теги (<p>, <div>) на двойной перенос (\n\n).
    # Это ключевой шаг, который создает разрывы между абзацами.
    text = re.sub(r'</p\s*>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</div\s*>', '\n\n', text, flags=re.IGNORECASE)
    
    # 2. Удаляем ссылки <a>...</a> целиком, включая их содержимое.
    text = re.sub(r'<a.*?>.*?</a>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # 3. Убираем ВСЕ остальные теги (включая открывающие <div>, <p>, <span>, <b> и т.д.)
    text = re.sub(r'<[^>]+>', '', text)
    
    # 4. Убираем множественные переносы, оставляя максимум два (для чистоты)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # 5. Очищаем пробелы и переносы с концов
    text = text.strip()
    
    return text