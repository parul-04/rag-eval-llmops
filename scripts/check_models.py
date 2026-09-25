from google.genai import errors
from rag.llm import client

candidates = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.7-flash", "gemini-3.8-flash"]

for model in candidates:
    try:
        client.models.generate_content(model=model, contents="Say OK")
        print(f"{model:28} OK")
    except errors.ClientError as e:   # 4xx: our side (not allowed, not found, quota)
        print(f"{model:28} {e.code} client error")
    except errors.ServerError as e:   # 5xx: their side (overloaded)
        print(f"{model:28} {e.code} server busy")