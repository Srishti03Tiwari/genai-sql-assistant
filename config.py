# config.py
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")   # keep for later
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_PATH        = os.getenv("DB_PATH", "./database/company.db")
FAISS_INDEX_PATH  = os.getenv("FAISS_INDEX_PATH",  "./faiss_index/index.faiss")
FAISS_CHUNKS_PATH = os.getenv("FAISS_CHUNKS_PATH", "./faiss_index/chunks.pkl")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "gemini-2.0-flash" 
TOP_K_CHUNKS    = 5