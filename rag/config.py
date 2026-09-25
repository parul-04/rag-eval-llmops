import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]   # fails loudly if missing
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")

settings = Settings()