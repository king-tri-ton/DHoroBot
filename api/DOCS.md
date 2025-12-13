# HoroAPI Documentation

## Класс `HoroAPI`

Парсер гороскопов с сайта [horo.mail.ru](https://horo.mail.ru/).
Возвращает **заголовок и очищенный текст** (HTML-теги и ссылки `<a>` удаляются).

### Инициализация

```python
from api.horo import HoroAPI

# ВСТАВЬТЕ СВОЙ User-Agent
user_agent = ""  
if not user_agent:
    user_agent = input("Введите User-Agent для парсера: ").strip()

horo = HoroAPI(user_agent)
```

* **user_agent** (str): User-Agent для HTTP-запросов. Обязателен.

---

### Методы

#### `fetch_page(url: str) -> tuple[str, str]`

Возвращает заголовок и текст гороскопа с указанной страницы.

* **url**: полная ссылка на страницу гороскопа.
* **Возвращает**: `(title, text)` — заголовок и очищенный текст.

#### `get_today_all() -> tuple[str, str]`

Гороскоп на сегодня для всех знаков.

* **Возвращает**: `(title, text)`.

#### `get_horo(sign: str, date: str) -> tuple[str, str]`

Гороскоп для конкретного знака и периода.

* **sign**: знак зодиака (значение для API, например `cancer`, `aries`).
* **date**: период (значение для API, например `today`, `week`).
* **Возвращает**: `(title, text)`.

---

### Значения знаков и периодов

**Знаки зодиака (ключи для API → отображение):**

```python
{
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
```

**Периоды:**

```python
{
    'yesterday': 'вчера',
    'today': 'сегодня',
    'tomorrow': 'завтра',
    'week': 'неделя',
    'month': 'месяц',
    'year': 'год'
}
```

---

### Примеры использования

```python
from api.horo import HoroAPI

# Инициализация
user_agent = input("Введите User-Agent: ").strip()
horo = HoroAPI(user_agent)

# Гороскоп на сегодня для всех знаков
title, text = horo.get_today_all()
print(title)
print(text)

# Гороскоп для Рака на сегодня
title, text = horo.get_horo("cancer", "today")
print(title)
print(text)
```

---

> Разработал [King Triton](https://github.com/king-tri-ton/)
