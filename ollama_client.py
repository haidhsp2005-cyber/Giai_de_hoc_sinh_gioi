import json
import httpx
from typing import AsyncGenerator, List, Dict, Any
from config import OLLAMA_BASE_URL, DEFAULT_THINKING_MODEL, DEFAULT_CODER_MODEL

class OllamaClient:
    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url.rstrip("/")

    async def check_health(self) -> bool:
        """Kiểm tra dịch vụ Ollama có đang chạy không"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def get_models(self) -> List[Dict[str, Any]]:
        """Lấy danh sách các model đang có sẵn trong Ollama"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = []
                    for m in data.get("models", []):
                        name = m.get("name", "")
                        size_gb = round(m.get("size", 0) / (1024**3), 2)
                        models.append({
                            "name": name,
                            "size": f"{size_gb} GB" if size_gb > 0 else "Cloud",
                            "details": m.get("details", {})
                        })
                    return models
                return []
        except Exception as e:
            print(f"Error fetching Ollama models: {e}")
            return []

    async def stream_generate(
        self,
        prompt: str,
        system: str = "",
        model: str = DEFAULT_THINKING_MODEL,
        temperature: float = 0.3
    ) -> AsyncGenerator[str, None]:
        """Gọi streaming generation từ Ollama"""
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": True,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "num_ctx": 8192
            }
        }
        
        url = f"{self.base_url}/api/generate"
        
        async with httpx.AsyncClient(timeout=600.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    yield f"\n[Lỗi kết nối Ollama (Status {response.status_code}): {error_text.decode('utf-8', errors='replace')}]\n"
                    return
                    
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("response", "")
                        if token:
                            yield token
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
