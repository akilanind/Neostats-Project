import os
import logging

# Configuration for CitizenHelp Assistant

try:
    from dotenv import load_dotenv
    # Resolve the absolute path to .env file in the project root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, ".env")
    
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        print(f"[config.py] Warning: .env file not found at {env_path}")

except ImportError:
    print("[config.py] Warning: 'python-dotenv' is not installed. Run: python setup_env.py to fix dependencies.")

# --- Constants & Environment Variables ---

try:
    # Essential for Groq LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Model configuration
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Vector storage
    CHROMA_DB_PATH: str = "./chroma_db"

    # Application details
    APP_NAME: str = "CitizenHelp — Government Scheme Assistant"

except Exception as e:
    print(f"[config.py] Error loading configuration: {e}")
    # Fallback defaults
    GROQ_API_KEY = ""
    GROQ_MODEL = "llama-3.3-70b-versatile"
    CHROMA_DB_PATH = "./chroma_db"
    APP_NAME = "CitizenHelp — Government Scheme Assistant"
