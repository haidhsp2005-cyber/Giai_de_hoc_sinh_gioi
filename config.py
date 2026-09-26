import os
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
ENV_FILE = BASE_DIR / ".env"

UPLOAD_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

def load_env_file(filepath: Path):
    """Tự động nạp file .env vào os.environ"""
    if not filepath.exists():
        return
    try:
        lines = filepath.read_text(encoding="utf-8").splitlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'").strip('"')
            if key and val:
                os.environ[key] = val
    except Exception as e:
        print(f"Lỗi đọc file .env: {e}")

# Nạp .env khi khởi động
load_env_file(ENV_FILE)

# Ollama API Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Default Models
DEFAULT_THINKING_MODEL = os.getenv("DEFAULT_OLLAMA_MODEL", "qwen2.5:7b")
DEFAULT_CODER_MODEL = "qwen2.5-coder:7b"
DEFAULT_GEMINI_MODEL = os.getenv("DEFAULT_GEMINI_MODEL", "gemini-3.6-flash")

# Gemini Keys from .env (hỗ trợ GEMINI_API_KEY_1, GEMINI_API_KEY_2, ..., GEMINI_API_KEYS và GEMINI_API_KEY)
def get_gemini_keys_from_env() -> List[str]:
    keys = []
    
    # 1. Quét các biến dạng GEMINI_API_KEY_1, GEMINI_API_KEY_2, GEMINI_API_KEY_3...
    numbered_keys = []
    for env_k, env_v in os.environ.items():
        if env_k.startswith("GEMINI_API_KEY_"):
            suffix = env_k.replace("GEMINI_API_KEY_", "")
            try:
                num = int(suffix)
            except ValueError:
                num = 9999
            clean_v = env_v.strip().strip("'").strip('"')
            if clean_v:
                numbered_keys.append((num, clean_v))
                
    # Sắp xếp đúng thứ tự 1, 2, 3, 4, 5...
    numbered_keys.sort(key=lambda x: x[0])
    for _, v in numbered_keys:
        if v and v not in keys:
            keys.append(v)

    # 2. Quét GEMINI_API_KEYS (danh sách nhiều key ngăn cách bằng dấu phẩy)
    keys_multi = os.getenv("GEMINI_API_KEYS", "")
    if keys_multi:
        for k in keys_multi.split(","):
            clean_k = k.strip().strip("'").strip('"')
            if clean_k and clean_k not in keys:
                keys.append(clean_k)

    # 3. Quét GEMINI_API_KEY (1 key đơn lẻ)
    key_single = os.getenv("GEMINI_API_KEY", "")
    if key_single:
        clean_s = key_single.strip().strip("'").strip('"')
        if clean_s and clean_s not in keys:
            keys.append(clean_s)

    return keys

ALLOWED_EXTENSIONS = {
    "docx": [".docx"],
    "pdf": [".pdf"],
    "image": [".png", ".jpg", ".jpeg", ".webp", ".bmp"]
}
