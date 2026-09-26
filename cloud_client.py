import json
import httpx
import asyncio
from typing import AsyncGenerator, Optional, List
from key_rotator import ApiKeyRotator

GEMINI_MODEL_FALLBACK_CHAIN = [
    "gemini-flash-latest",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-flash-lite-latest"
]

class CloudClient:
    """
    Client kết nối dịch vụ AI Đám mây (Gemini, DeepSeek, OpenAI)
    Hỗ trợ:
    1. Xoay vòng API Key (Round-Robin & Auto-Failover on 429)
    2. Tự động chuyển đổi mô hình dự phòng khi gặp lỗi 503 (High Demand) hoặc 404 (Deprecated)
    """
    def __init__(self, rotator: ApiKeyRotator):
        self.rotator = rotator

    async def stream_gemini(
        self,
        prompt: str,
        system_prompt: str = "",
        model: str = "gemini-3.6-flash",
        temperature: float = 0.2
    ) -> AsyncGenerator[str, None]:
        """
        Gọi Google Gemini API với cơ chế tự động xoay vòng key và tự động chuyển model dự phòng khi 503/404
        """
        models_to_try = [model]
        for m in GEMINI_MODEL_FALLBACK_CHAIN:
            if m not in models_to_try:
                models_to_try.append(m)

        max_key_attempts = max(1, len(self.rotator.pools.get("gemini", [])))
        key_attempts = 0
        current_model_idx = 0

        while current_model_idx < len(models_to_try):
            active_model = models_to_try[current_model_idx]

            key_data = self.rotator.get_next_key("gemini")
            if not key_data:
                yield "\n[Lỗi: Chưa cấu hình Gemini API Key hoặc tất cả các key đều đang trong thời gian chờ (Cooldown). Vui lòng vào Cấu hình API Key để bổ sung.]\n"
                return

            api_key, key_idx = key_data
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{active_model}:streamGenerateContent?alt=sse&key={api_key}"

            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt}]
                    }
                ],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": 8192
                }
            }
            if system_prompt:
                payload["systemInstruction"] = {
                    "parts": [{"text": system_prompt}]
                }

            headers = {"Content-Type": "application/json"}

            try:
                async with httpx.AsyncClient(timeout=300.0) as client:
                    async with client.stream("POST", url, json=payload, headers=headers) as response:
                        # 1. Xử lý lỗi 503 Quá tải (High Demand)
                        if response.status_code in [503, 500, 502, 504]:
                            print(f"[Gemini 503] Model {active_model} quá tải, thử model dự phòng...")
                            current_model_idx += 1
                            if current_model_idx < len(models_to_try):
                                next_model = models_to_try[current_model_idx]
                                yield f"\n*(Model [{active_model}] đang quá tải 503. Tự động chuyển sang mô hình dự phòng [{next_model}]...)*\n\n"
                                await asyncio.sleep(0.5)
                                continue
                            else:
                                yield f"\n[Thông báo: Tất cả cụm máy chủ Gemini hiện đang quá tải (503). Vui lòng chuyển sang dùng mô hình Ollama Local.]\n"
                                return

                        # 2. Xử lý lỗi 404
                        elif response.status_code == 404:
                            print(f"[Gemini 404] Model {active_model} không hỗ trợ, thử model tiếp...")
                            current_model_idx += 1
                            if current_model_idx < len(models_to_try):
                                next_model = models_to_try[current_model_idx]
                                yield f"\n*(Model [{active_model}] không còn hỗ trợ. Chuyển sang [{next_model}]...)*\n\n"
                                continue
                            else:
                                yield f"\n[Lỗi: Không tìm thấy model Gemini phù hợp.]\n"
                                return

                        # 3. Xử lý lỗi 429 Rate Limit
                        elif response.status_code in [429, 403]:
                            self.rotator.mark_rate_limited("gemini", api_key, cooldown_seconds=60)
                            key_attempts += 1
                            if key_attempts < max_key_attempts:
                                yield f"\n*(Key Gemini #{key_idx + 1} đạt giới hạn tốc độ 429. Tự động xoay vòng sang Key tiếp theo...)*\n\n"
                                continue
                            else:
                                yield f"\n[Lỗi: Tất cả API Keys đều đang đạt giới hạn hạn mức (429). Vui lòng đợi 1 phút hoặc dùng Ollama Local.]\n"
                                return

                        elif response.status_code != 200:
                            err_body = await response.aread()
                            yield f"\n[Lỗi Gemini API (Status {response.status_code}): {err_body.decode('utf-8', errors='replace')[:200]}]\n"
                            return

                        # Thành công!
                        self.rotator.mark_success("gemini", api_key)

                        async for line in response.aiter_lines():
                            if not line:
                                continue
                            if line.startswith("data: "):
                                json_str = line[6:].strip()
                                try:
                                    chunk = json.loads(json_str)
                                    candidates = chunk.get("candidates", [])
                                    if candidates:
                                        parts = candidates[0].get("content", {}).get("parts", [])
                                        for part in parts:
                                            text = part.get("text", "")
                                            if text:
                                                yield text
                                except json.JSONDecodeError:
                                    continue
                return

            except httpx.RequestError as e:
                yield f"\n[Lỗi kết nối mạng: {str(e)}]\n"
                return

    async def stream_openai_compatible(
        self,
        prompt: str,
        system_prompt: str = "",
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com/v1",
        provider: str = "deepseek",
        temperature: float = 0.2
    ) -> AsyncGenerator[str, None]:
        max_attempts = max(1, len(self.rotator.pools.get(provider, [])))
        attempts = 0

        while attempts < max_attempts:
            key_data = self.rotator.get_next_key(provider)
            if not key_data:
                yield f"\n[Lỗi: Chưa cấu hình API Key cho {provider.upper()}.]\n"
                return

            api_key, key_idx = key_data
            attempts += 1

            url = f"{base_url.rstrip('/')}/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": model,
                "messages": messages,
                "stream": True,
                "temperature": temperature
            }

            try:
                async with httpx.AsyncClient(timeout=300.0) as client:
                    async with client.stream("POST", url, json=payload, headers=headers) as response:
                        if response.status_code in [429, 503]:
                            self.rotator.mark_rate_limited(provider, api_key, cooldown_seconds=60)
                            if attempts < max_attempts:
                                yield f"\n*(Key #{key_idx + 1} bị quá tải ({response.status_code}). Đang chuyển tiếp sang key kế tiếp...)*\n\n"
                                continue
                            else:
                                yield "\n[Lỗi: Toàn bộ API Key đều đang bị giới hạn hạn mức.]\n"
                                return

                        elif response.status_code != 200:
                            err_text = await response.aread()
                            yield f"\n[Lỗi {provider.upper()} API (Status {response.status_code}): {err_text.decode('utf-8', errors='replace')[:200]}]\n"
                            return

                        self.rotator.mark_success(provider, api_key)

                        async for line in response.aiter_lines():
                            if not line:
                                continue
                            if line.startswith("data: "):
                                data_str = line[6:].strip()
                                if data_str == "[DONE]":
                                    break
                                try:
                                    chunk = json.loads(data_str)
                                    choices = chunk.get("choices", [])
                                    if choices:
                                        delta = choices[0].get("delta", {})
                                        content = delta.get("content", "")
                                        if content:
                                            yield content
                                except json.JSONDecodeError:
                                    continue
                return

            except httpx.RequestError as e:
                yield f"\n[Lỗi kết nối tới {provider.upper()}: {str(e)}]\n"
                return
