"""Central configuration. Loaded once at import time from .env."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Paths ---
ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "scraper.db"

# --- LLM (DeepSeek) ---
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY not found. Copy .env.example to .env and fill it in.")

LLM_PROVIDER = "deepseek/deepseek-chat"
LLM_BASE_URL = "https://api.deepseek.com/v1"
LLM_TEMPERATURE = 0.1

# --- Discovery APIs ---
OPENALEX_EMAIL = os.getenv("OPENALEX_EMAIL", "")  # optional but recommended
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
CORE_API_KEY = os.getenv("CORE_API_KEY", "")  # core.ac.uk — 200M+ open access papers

# --- Pipeline tuning ---
DEFAULT_DISCOVERY_LIMIT = 30      # per provider, before merge
DEFAULT_MAX_PAPERS = 10           # how many papers Phase 2 deeply extracts
RELEVANCE_THRESHOLD = 0.4
CRAWLER_TIMEOUT_MS = 45_000
CRAWLER_WORD_THRESHOLD = 10
HTTP_TIMEOUT = 30.0
HTTP_RETRIES = 3

# --- Server ---
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# --- Languages supported by post-extraction translation ---
SUPPORTED_LANGUAGES = {"en": "English", "ua": "Ukrainian"}
