import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.1-flash")

settings = Settings()