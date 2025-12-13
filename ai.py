from openai import OpenAI
from config import OPENAI_API_KEY
from utils import md_to_html

client = OpenAI(api_key=OPENAI_API_KEY)

def get_openai_response(message: str):
    """
    Генерирует текст через GPT-4.1-mini.
    Возвращает текст и токены (prompt, completion).
    """
    model = "gpt-4.1-mini"
    try:
        result = client.responses.create(
            model=model,
            input=message
        )
        text = md_to_html(result.output_text)
        usage = getattr(result, "usage", None)
        prompt_tokens = getattr(usage, "input_tokens", 0)
        completion_tokens = getattr(usage, "output_tokens", 0)
        return text, prompt_tokens, completion_tokens

    except Exception as e:
        print(f"ОШИБКА в get_openai_response: {e}")
        import traceback
        traceback.print_exc()
        return f"Ошибка при обращении к API: {e}", 0, 0


def build_personal_horoscope_prompt(name: str, birthdate: str, period_key: str, period_text: str):
    """
    Формирует prompt для персонального гороскопа.
    """
    return (
        f"Составь персональный гороскоп для пользователя {name}, "
        f"Определи его знак зодиака по дате рождения {birthdate}, "
        f"на период {period_text}. "
        f"Текст должен быть дружелюбным, лаконичным, на русском языке, "
        f"немного с эмодзи и не используй символ длинное тире, "
        f"добавь пару советов дополни свой ответ."
    )
