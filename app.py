import os
import json
import uuid
import shutil
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import UPLOAD_DIR, STATIC_DIR, TEMPLATES_DIR, DEFAULT_THINKING_MODEL, DEFAULT_CODER_MODEL
from document_parser import extract_problem_content
from prompt_templates import SYSTEM_PROMPT_HSG, USER_PROMPT_TEMPLATE
from ollama_client import OllamaClient
from key_rotator import ApiKeyRotator
from cloud_client import CloudClient
from agent_engine import MultiAgentSolver, AGENT_STEPS

app = FastAPI(title="HSG Solver AI - Giải Đề Học Sinh Giỏi Tin Học (Dual Engine)", version="3.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

ollama = OllamaClient()
key_rotator = ApiKeyRotator(storage_file=UPLOAD_DIR / "api_keys.json")
cloud_client = CloudClient(key_rotator)
multi_agent = MultiAgentSolver(ollama, cloud_client)

SAMPLE_PROBLEMS = [
    {
        "id": "subset_sum",
        "title": "Dãy con có tổng bằng S (SUBSET)",
        "source": "Đề thi HSG Tỉnh lớp 12",
        "text": """Cho dãy số nguyên A gồm N phần tử A1, A2, ..., AN và một số nguyên dương S.
Hãy tìm một dãy con (không nhất thiết liên tiếp) các phần tử của dãy A sao cho tổng các phần tử đúng bằng S. Nếu có nhiều dãy con thỏa mãn, hãy in ra dãy con có số phần tử ít nhất. Nếu không có, in ra -1.

Dữ liệu vào (SUBSET.INP):
- Dòng đầu ghi 2 số nguyên N và S (1 <= N <= 100, 1 <= S <= 100000).
- Dòng thứ hai ghi N số nguyên A1, A2, ..., AN (1 <= Ai <= 10000).

Dữ liệu ra (SUBSET.OUT):
- In ra số phần tử của dãy con tìm được, nếu không có in ra -1.

Ràng buộc subtask:
- Subtask 1 (30% số điểm): N <= 20, S <= 100.
- Subtask 2 (30% số điểm): N <= 50, S <= 1000.
- Subtask 3 (40% số điểm): N <= 100, S <= 100000.

Ví dụ:
Input:
5 12
2 3 5 7 10
Output:
2
(Giải thích: Chọn 2 phần tử {5, 7} có tổng 5 + 7 = 12 -> 2 phần tử)."""
    },
    {
        "id": "max_subarray",
        "title": "Đoạn con có tổng lớn nhất (MAXSUB)",
        "source": "Đề thi Olympic Tin học Miền Trung & Tây Nguyên",
        "text": """Cho một dãy số nguyên A gồm N phần tử: a1, a2, ..., aN.
Một đoạn con của dãy A là một dãy liên tiếp các phần tử ai, ai+1, ..., aj với 1 <= i <= j <= N.
Trọng số của một đoạn con là tổng tất cả các phần tử trong đoạn con đó.
Yêu cầu: Hãy tìm đoạn con có trọng số lớn nhất.

Dữ liệu vào:
- Dòng thứ nhất chứa số nguyên N (1 <= N <= 10^6).
- Dòng thứ hai chứa N số nguyên a1, a2, ..., aN (|ai| <= 10^9).

Dữ liệu ra:
- Một số nguyên duy nhất là trọng số lớn nhất của đoạn con tìm được.

Ràng buộc:
- Subtask 1 (30% số điểm): N <= 500.
- Subtask 2 (30% số điểm): N <= 5000.
- Subtask 3 (40% số điểm): N <= 10^6.

Ví dụ:
Input:
6
-2 1 -3 4 -1 2
Output:
5
(Đoạn con [4, -1, 2] có tổng lớn nhất là 4 + (-1) + 2 = 5)."""
    },
    {
        "id": "binary_search_wood",
        "title": "Cắt gỗ lấy củi (EKO)",
        "source": "Đề thi HSG Quốc Gia / SPOJ",
        "text": """Mirko cần chặt một lượng gỗ có tổng chiều dài ít nhất là M mét. Thiết bị của Mirko là một máy cắt gỗ hoạt động như sau: Mirko thiết lập một thông số chiều cao H (mét). Máy sẽ cắt tất cả các cây cao hơn H, phần ngọn cây cao hơn H sẽ bị cắt đứt và rơi xuống đất, phần thân cây có chiều cao <= H sẽ được giữ nguyên.
Mirko muốn tìm chiều cao H nguyên lớn nhất có thể thiết lập sao cho tổng lượng gỗ thu được ít nhất là M mét.

Dữ liệu vào:
- Dòng đầu chứa hai số nguyên dương N và M (1 <= N <= 10^6, 1 <= M <= 2*10^9).
- Dòng thứ hai chứa N số nguyên dương là chiều cao của N cái cây, mỗi cây có chiều cao không quá 10^9 mét.

Dữ liệu ra:
- Chiều cao nguyên H lớn nhất cần tìm.

Giới hạn:
- Subtask 1 (20% số điểm): N <= 1000, M <= 10^4, chiều cao cây <= 10^4.
- Subtask 2 (30% số điểm): N <= 10^5, M <= 10^9.
- Subtask 3 (50% số điểm): N <= 10^6, M <= 2*10^9.

Ví dụ:
Input:
4 7
20 15 10 17
Output:
15
(Nếu H = 15, các cây bị cắt lần lượt được: max(0, 20-15) = 5; max(0, 15-15) = 0; max(0, 10-15) = 0; max(0, 17-15) = 2. Tổng lượng gỗ = 5 + 0 + 0 + 2 = 7 mét)."""
    }
]

class SolveRequest(BaseModel):
    problem_text: str
    model: str = DEFAULT_THINKING_MODEL
    provider: str = "ollama"  # "ollama", "gemini", "deepseek"
    mode: str = "agent"       # "agent" (Multi-Agent Pro) or "fast"
    temperature: float = 0.2

class KeyUpdateRequest(BaseModel):
    provider: str
    keys: List[str]

@app.get("/", response_class=FileResponse)
async def index():
    index_file = TEMPLATES_DIR / "index.html"
    return FileResponse(str(index_file), media_type="text/html")

@app.get("/api/health")
async def health():
    is_healthy = await ollama.check_health()
    gemini_status = key_rotator.get_status("gemini")
    deepseek_status = key_rotator.get_status("deepseek")
    return {
        "status": "ok",
        "ollama": is_healthy,
        "cloud": {
            "gemini": gemini_status,
            "deepseek": deepseek_status
        }
    }


@app.get("/api/env-status")
async def env_status():
    key_rotator.reload_env_keys()
    gemini_status = key_rotator.get_status("gemini")
    is_ollama_healthy = await ollama.check_health()
    return {
        "gemini_keys_count": gemini_status.get("total_keys", 0),
        "gemini_active_keys": gemini_status.get("active_keys", 0),
        "gemini_loaded": gemini_status.get("total_keys", 0) > 0,
        "ollama_available": is_ollama_healthy
    }

@app.post("/api/env/reload")
async def env_reload():
    key_rotator.reload_env_keys()
    gemini_keys = [item["key"] for item in key_rotator.pools.get("gemini", []) if item.get("key")]
    return {
        "success": True,
        "status": key_rotator.get_status("gemini"),
        "gemini_keys": gemini_keys
    }

@app.get("/api/keys")
async def get_keys():
    gemini_keys = [item["key"] for item in key_rotator.pools.get("gemini", []) if item.get("key")]
    return {
        "gemini": key_rotator.get_status("gemini"),
        "gemini_keys": gemini_keys,
        "deepseek": key_rotator.get_status("deepseek"),
        "openai": key_rotator.get_status("openai")
    }

@app.post("/api/keys")
async def save_keys(req: KeyUpdateRequest):
    key_rotator.set_keys(req.provider, req.keys)
    if req.provider.lower() == "gemini":
        key_rotator.save_gemini_keys_to_env()
    gemini_keys = [item["key"] for item in key_rotator.pools.get(req.provider.lower(), []) if item.get("key")]
    return {
        "success": True,
        "status": key_rotator.get_status(req.provider),
        "gemini_keys": gemini_keys
    }

@app.get("/api/models")
async def get_models():
    ollama_models = await ollama.get_models()
    
    # Online models
    online_models = [
        {"name": "gemini-3.6-flash", "provider": "gemini", "desc": "Google Gemini 2.5 Flash (Siêu nhanh, xoay vòng Key)"},
        {"name": "gemini-1.5-pro", "provider": "gemini", "desc": "Google Gemini 1.5 Pro (Tư duy toán học sâu)"},
        {"name": "deepseek-chat", "provider": "deepseek", "desc": "DeepSeek V3 (Thông minh, hỗ trợ lập trình)"},
        {"name": "deepseek-reasoner", "provider": "deepseek", "desc": "DeepSeek R1 (Lập luận sâu, suy diễn logic)"}
    ]

    return {
        "ollama_models": ollama_models,
        "online_models": online_models,
        "recommended": [DEFAULT_THINKING_MODEL, DEFAULT_CODER_MODEL],
        "default_thinking": DEFAULT_THINKING_MODEL,
        "default_coder": DEFAULT_CODER_MODEL
    }

@app.get("/api/agent-steps")
async def get_agent_steps():
    return {"steps": AGENT_STEPS}

@app.get("/api/samples")
async def get_samples():
    return {"samples": SAMPLE_PROBLEMS}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    save_path = UPLOAD_DIR / unique_name
    
    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        result = extract_problem_content(save_path)
        return {
            "success": True,
            "filename": filename,
            "file_type": result.get("file_type", "unknown"),
            "content": result.get("content", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi đọc file: {str(e)}")

@app.post("/api/solve")
async def solve_problem(req: SolveRequest):
    if not req.problem_text.strip():
        raise HTTPException(status_code=400, detail="Vui lòng nhập hoặc tải lên đề bài.")

    async def event_generator():
        try:
            if req.mode == "agent":
                # Chế độ Đa Agent (Hỗ trợ cả Ollama và Cloud AI xoay vòng key)
                async for event in multi_agent.run_agent_pipeline(
                    problem_text=req.problem_text,
                    preferred_model=req.model,
                    provider=req.provider,
                    temperature=req.temperature
                ):
                    data = json.dumps(event, ensure_ascii=False)
                    yield f"data: {data}\n\n"
            else:
                # Chế độ giải nhanh (Fast Mode)
                formatted_user_prompt = USER_PROMPT_TEMPLATE.replace("{problem_text}", req.problem_text)
                
                if req.provider == "gemini":
                    stream = cloud_client.stream_gemini(
                        prompt=formatted_user_prompt,
                        system_prompt=SYSTEM_PROMPT_HSG,
                        model=req.model if "gemini" in req.model else "gemini-3.6-flash",
                        temperature=req.temperature
                    )
                elif req.provider == "deepseek":
                    stream = cloud_client.stream_openai_compatible(
                        prompt=formatted_user_prompt,
                        system_prompt=SYSTEM_PROMPT_HSG,
                        model=req.model if "deepseek" in req.model else "deepseek-chat",
                        provider="deepseek",
                        temperature=req.temperature
                    )
                else:
                    stream = ollama.stream_generate(
                        prompt=formatted_user_prompt,
                        system=SYSTEM_PROMPT_HSG,
                        model=req.model,
                        temperature=req.temperature
                    )

                async for token in stream:
                    data = json.dumps({"type": "token", "content": token}, ensure_ascii=False)
                    yield f"data: {data}\n\n"
                    
                yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            err_data = json.dumps({"type": "error", "message": str(e)}, ensure_ascii=False)
            yield f"data: {err_data}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
