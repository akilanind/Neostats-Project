import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    CHROMA_DB_PATH: str = "./chroma_db"

    APP_NAME: str = "CitizenHelp — Government Scheme Assistant"

except Exception as e:
    print(f"[config.py] Warning: Failed to load one or more config values. Error: {e}")
    GROQ_API_KEY = ""
    GROQ_MODEL = "llama-3.3-70b-versatile"
    CHROMA_DB_PATH = "./chroma_db"
    APP_NAME = "CitizenHelp — Government Scheme Assistant"
