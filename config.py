from dotenv import load_dotenv
import os

load_dotenv()

TOKEN			= os.getenv("TOKEN")
ADMIN			= int(os.getenv("ADMIN", "0"))
BOT_LINK		= os.getenv("BOT_LINK")
USER_AGENT		= os.getenv("USER_AGENT")
UTC				= int(os.getenv("UTC", "0"))
OPENAI_API_KEY	= os.getenv("OPENAI_API_KEY")
