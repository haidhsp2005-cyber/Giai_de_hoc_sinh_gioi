import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from config import get_gemini_keys_from_env

class ApiKeyRotator:
    """
    Bộ điều phối và xoay vòng API Keys (Round-Robin & Auto-Failover on 429)
    Tự động nạp keys từ file .env và lưu trữ phiên.
    """
    def __init__(self, storage_file: Optional[Path] = None):
        self.storage_file = storage_file
        self.pools: Dict[str, List[Dict]] = {
            "gemini": [],
            "deepseek": [],
            "openai": []
        }
        self.current_index: Dict[str, int] = {
            "gemini": 0,
            "deepseek": 0,
            "openai": 0
        }
        
        # 1. Nạp keys từ file JSON đã lưu nếu có
        if self.storage_file and self.storage_file.exists():
            self.load_keys()

        # 2. Tự động nạp và gộp keys từ .env
        env_keys = get_gemini_keys_from_env()
        if env_keys:
            existing_keys = [it["key"] for it in self.pools.get("gemini", [])]
            for ek in env_keys:
                if ek not in existing_keys:
                    self.add_single_key("gemini", ek)

    def reload_env_keys(self):
        """Quét lại keys từ file .env và đồng bộ chính xác"""
        from config import load_env_file, ENV_FILE
        load_env_file(ENV_FILE)
        env_keys = get_gemini_keys_from_env()
        if env_keys:
            self.set_keys("gemini", env_keys)

    def add_single_key(self, provider: str, key: str):
        provider = provider.lower()
        if provider not in self.pools:
            self.pools[provider] = []
        self.pools[provider].append({
            "key": key.strip(),
            "cooldown_until": 0.0,
            "usage_count": 0,
            "error_count": 0
        })

    def set_keys(self, provider: str, keys: List[str]):
        """Cập nhật danh sách key cho một provider"""
        provider = provider.lower()
        cleaned_keys = [k.strip() for k in keys if k.strip()]
        existing = {item["key"]: item for item in self.pools.get(provider, [])}
        
        new_pool = []
        for k in cleaned_keys:
            if k in existing:
                new_pool.append(existing[k])
            else:
                new_pool.append({
                    "key": k,
                    "cooldown_until": 0.0,
                    "usage_count": 0,
                    "error_count": 0
                })
        self.pools[provider] = new_pool
        self.current_index[provider] = 0
        if self.storage_file:
            self.save_keys()

    def save_gemini_keys_to_env(self, filepath: Optional[Path] = None):
        """Lưu danh sách key Gemini hiện tại vào file .env theo định dạng GEMINI_API_KEY_1, 2, ..."""
        if filepath is None:
            from config import ENV_FILE
            filepath = ENV_FILE
        
        gemini_keys = [item["key"] for item in self.pools.get("gemini", []) if item.get("key")]
        lines = [
            "# ==============================================================================",
            "# CẤU HÌNH API KEYS GOOGLE GEMINI TỰ ĐỘNG XOAY VÒNG",
            "# ==============================================================================",
            ""
        ]
        for idx, k in enumerate(gemini_keys, start=1):
            lines.append(f'GEMINI_API_KEY_{idx}="{k}"')
        
        lines.extend([
            "",
            "# Cấu hình Ollama Local & Model mặc định",
            "OLLAMA_BASE_URL=http://localhost:11434",
            "DEFAULT_GEMINI_MODEL=gemini-flash-latest",
            ""
        ])
        filepath.write_text("\n".join(lines), encoding="utf-8")

    def get_next_key(self, provider: str) -> Optional[Tuple[str, int]]:
        """
        Lấy key tiếp theo theo cơ chế Round-Robin.
        Bỏ qua các key đang trong thời gian Cooldown (bị 429).
        """
        provider = provider.lower()
        pool = self.pools.get(provider, [])
        if not pool:
            return None

        now = time.time()
        n = len(pool)
        start_idx = self.current_index.get(provider, 0) % n

        # Duyệt qua các key để tìm key sẵn sàng
        for offset in range(n):
            idx = (start_idx + offset) % n
            item = pool[idx]
            if item["cooldown_until"] <= now:
                self.current_index[provider] = (idx + 1) % n
                return item["key"], idx

        # Nếu tất cả các key đều đang cooldown, lấy key có cooldown sắp hết nhất
        best_idx = min(range(n), key=lambda i: pool[i]["cooldown_until"])
        return pool[best_idx]["key"], best_idx

    def mark_rate_limited(self, provider: str, key: str, cooldown_seconds: int = 60):
        """Đánh dấu key bị dính giới hạn cước (HTTP 429 Too Many Requests)"""
        provider = provider.lower()
        pool = self.pools.get(provider, [])
        now = time.time()
        for item in pool:
            if item["key"] == key:
                item["cooldown_until"] = now + cooldown_seconds
                item["error_count"] += 1
                break

    def mark_success(self, provider: str, key: str):
        """Ghi nhận lượt gọi thành công"""
        provider = provider.lower()
        pool = self.pools.get(provider, [])
        for item in pool:
            if item["key"] == key:
                item["usage_count"] += 1
                item["cooldown_until"] = 0.0
                break

    def get_status(self, provider: str) -> Dict:
        """Lấy thông tin trạng thái pool keys"""
        provider = provider.lower()
        pool = self.pools.get(provider, [])
        now = time.time()

        keys_info = []
        active_count = 0
        cooldown_count = 0

        for item in pool:
            k = item["key"]
            masked = k[:6] + "..." + k[-4:] if len(k) > 10 else "***"
            is_cooling = item["cooldown_until"] > now
            remaining_cooldown = max(0, int(item["cooldown_until"] - now)) if is_cooling else 0

            if is_cooling:
                cooldown_count += 1
                status = "cooldown"
            else:
                active_count += 1
                status = "ready"

            keys_info.append({
                "masked": masked,
                "status": status,
                "remaining_cooldown": remaining_cooldown,
                "usage_count": item["usage_count"],
                "error_count": item["error_count"]
            })

        return {
            "provider": provider,
            "total_keys": len(pool),
            "active_keys": active_count,
            "cooldown_keys": cooldown_count,
            "keys": keys_info
        }

    def save_keys(self):
        """Lưu danh sách keys vào file JSON để dùng lại"""
        if not self.storage_file:
            return
        try:
            data = {}
            for prov, items in self.pools.items():
                data[prov] = [it["key"] for it in items]
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)
            self.storage_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"Lỗi lưu file API keys: {e}")

    def load_keys(self):
        """Đọc keys đã lưu từ file JSON"""
        if not self.storage_file or not self.storage_file.exists():
            return
        try:
            content = self.storage_file.read_text(encoding="utf-8")
            data = json.loads(content)
            for prov, keys in data.items():
                if isinstance(keys, list):
                    self.set_keys(prov, keys)
        except Exception as e:
            print(f"Lỗi đọc file API keys: {e}")
