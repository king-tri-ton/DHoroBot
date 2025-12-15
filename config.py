from dotenv import load_dotenv
import os

load_dotenv()

def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Переменная окружения {name} не задана")
    return value

TOKEN				= require_env("TOKEN")
OPENAI_API_KEY		= require_env("OPENAI_API_KEY")
HOROSCOPE_PROMPT	= require_env("HOROSCOPE_PROMPT")

ADMIN		= int(os.getenv("ADMIN", "0"))
BOT_LINK	= os.getenv("BOT_LINK")
USER_AGENT	= os.getenv("USER_AGENT")
UTC			= int(os.getenv("UTC", "0"))
