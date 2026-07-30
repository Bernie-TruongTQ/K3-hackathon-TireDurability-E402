import torch
import os
from dotenv import load_dotenv
load_dotenv()
CONFIG = {
    # Chọn Provider: "qwen" (chạy local) hoặc "gemini" (gọi API)
    "llm_provider": os.getenv("LLM_PROVIDER"),
    "db_path": "db_ds",
    "collection_name": "slide_ds",
    "embedding_model": "Qwen/Qwen3-Embedding-0.6B",
    "reranker_model": "BAAI/bge-reranker-v2-m3",
    "llm_model": "Qwen/Qwen3-0.6B",
    # "llm_model": "Qwen/Qwen3-4B-Instruct-2507",
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "retrieval_k": 50,  # Số lượng doc lấy từ VectorDB
    "rerank_top_k": 5,  # Số lượng doc tốt nhất sau khi Re-rank để đưa vào LLM
    # Cấu hình Qwen (Local)
    "local_model_path": "Qwen/Qwen3-0.6B",
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "max_new_tokens": int(os.getenv("LLM_MAX_TOKENS")),
    "temperature": float(os.getenv("LLM_TEMPERATURE")),
    # Cấu hình Gemini (API)
    "google_api_key": os.getenv("GOOGLE_API_KEY"),
    "gemini_model_name": os.getenv("GEMINI_MODEL_NAME"),
}