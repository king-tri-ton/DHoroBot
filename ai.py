from openai import OpenAI
from config import OPENAI_API_KEY, HOROSCOPE_PROMPT
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
    try:
        return HOROSCOPE_PROMPT.format(
            name=name,
            birthdate=birthdate,
            period_text=period_text
        )
    except KeyError as e:
        raise RuntimeError(f"В шаблоне HOROSCOPE_PROMPT не хватает переменной: {e}")
