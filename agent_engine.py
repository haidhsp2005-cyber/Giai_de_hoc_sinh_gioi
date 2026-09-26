"""
HSG Multi-Agent Orchestrator (Đội ngũ AI Agent Chuyên Nghiệp Giải Đề HSG Tin Học)
Hỗ trợ chạy trên cả Ollama Cục bộ và Đám mây Online (Gemini/DeepSeek với xoay vòng key).
"""

import json
from typing import AsyncGenerator, Dict, Any, List, Optional
from config import DEFAULT_THINKING_MODEL, DEFAULT_CODER_MODEL
from ollama_client import OllamaClient
from cloud_client import CloudClient

AGENT_STEPS = [
    {
        "id": "step_1_analysis",
        "name": "Thẩm định Đề bài & Bẫy Dữ liệu",
        "agent": "ConstraintAnalyst",
        "icon": "search",
        "description": "Quét biến số, phân tích bẫy tràn số (long long), giới hạn thời gian và phân chia Subtasks."
    },
    {
        "id": "step_2_algorithm",
        "name": "Thiết kế Giải thuật & Toán học",
        "agent": "AlgorithmArchitect",
        "icon": "lightbulb",
        "description": "Xây dựng ý tưởng thuật toán từ vét cạn (30%) đến thuật toán tối ưu chuẩn (100% điểm)."
    },
    {
        "id": "step_3_coding",
        "name": "Lập trình C++ & Python 3",
        "agent": "CompetitiveCoder",
        "icon": "code-2",
        "description": "Viết mã nguồn C++ chuẩn Fast I/O và Python 3 tối ưu I/O/đệ quy, chú thích chi tiết."
    },
    {
        "id": "step_4_testing",
        "name": "Thẩm định Test & Test Generator",
        "agent": "TestEngineer",
        "icon": "flask-conical",
        "description": "Giải thích test mẫu đề bài, thiết kế edge cases và viết script Python Stress Test."
    },
    {
        "id": "step_5_review",
        "name": "Tự động Phản biện & Hoàn thiện",
        "agent": "ReviewerAuditor",
        "icon": "shield-check",
        "description": "Rà soát lỗi tiềm ẩn (tràn số, off-by-one, TLE) và tổng hợp bản lời giải tối ưu nhất."
    }
]

PROMPT_MULTI_AGENT_SYNTHESIS = r"""Bạn là Trưởng ban Giám khảo Olympic Tin học Quốc gia (VNOI / IOI) dẫn dắt Đội đồng 5 Chuyên gia AI.
Đề bài Học Sinh Giỏi Tin Học cần giải quyết:

--- NỘI DUNG ĐỀ BÀI ---
{problem_text}
-----------------------

Hội đồng chuyên gia của bạn gồm có:
1. Chuyên gia Thẩm định Đề bài & Bẫy dữ liệu (ConstraintAnalyst)
2. Kiến trúc sư Giải thuật & Toán học (AlgorithmArchitect)
3. Lập trình viên Thi đấu C++ & Python (CompetitiveCoder)
4. Chuyên gia Thẩm định Test & Stress Testing (TestEngineer)
5. Giám khảo Tự động Phản biện & Tối ưu (ReviewerAuditor)

Nhiệm vụ: Hãy phối hợp tri thức của cả 5 chuyên gia trên để tạo ra BẢN LỜI GIẢI ĐẠT CHUẨN 100% ĐIỂM TUYỆT ĐỐI.
Yêu cầu bạn PHẢI tuân thủ nghiêm ngặt các quy tắc chuyên sâu:
1. **RÀ SOÁT BẪY DỮ LIỆU CỰC KỲ KHẮT KHE**:
   - Nếu A_i, N >= 10^9 hoặc tích các số có thể vượt 2*10^9, bắt buộc dùng long long trong C++!
   - Nếu 10^18, kiểm tra tràn số khi cộng nhân.
   - Nhận diện các trường hợp biên đặc biệt (Corner cases): N=1, N=0, giá trị âm, mảng toàn phần tử bằng nhau.
2. **PHÂN CHIA SUBTASK RÕ RÀNG**:
   - Subtask 1: Vét cạn / Cơ bản (30% điểm) cho N nhỏ.
   - Subtask 2: Thuật toán cải tiến (30% điểm).
   - Subtask 3: Thuật toán Tối ưu chuẩn (Full 100% điểm) đạt O(N log N) hoặc O(N) dưới 1.0 giây.
3. **MÃ NGUỒN CHUẨN MỰC**:
   - C++: Có ios_base::sync_with_stdio(false); cin.tie(NULL);, hỗ trợ freopen nếu đề có tên file, xử lý tràn số long long.
   - Python 3: Dùng sys.stdin.readline và sys.setrecursionlimit(10**6).
4. **THẨM ĐỊNH TEST & SINH TEST NGẪU NHIÊN**:
   - Giải thích từng bước vì sao Input của đề lại cho ra Output mẫu.
   - Bảng test cases mở rộng (các trường hợp biên hiểm hóc).
   - Script Python sinh test ngẫu nhiên (test_gen.py) để học sinh làm Stress Test.
5. **ĐÁNH GIÁ PHẢN BIỆN (SELF-REFLECTION)**:
   - Ghi chú các lỗi học sinh thường mắc phải (Common Pitfalls) và cách phòng tránh.

Hãy xuất bản toàn bộ lời giải theo định dạng Markdown chi tiết sau:

# [TÊN BÀI TOÁN HOẶC MÃ ĐỀ THI]

> 🛡️ **BÁO CÁO THẨM ĐỊNH TỪ HỘI ĐỒNG CHUYÊN GIA AI HSG PRO**
> - **Độ khó ước tính:** [Cơ bản / Trung bình / HSG Tỉnh / HSG Quốc Gia / Olympic]
> - **Cấu trúc dữ liệu & Thuật toán chính:** [Ví dụ: Quy hoạch động, Cây phân đoạn, Hai con trỏ, v.v.]
> - **Cảnh báo bẫy dữ liệu (Critical Warnings):** [Ví dụ: Bắt buộc dùng long long vì tổng có thể lên tới 10^14; cẩn thận trường hợp N=1].

---

## 1. TÓM TẮT ĐỀ BÀI & RÀNG BUỘC
- **Tên bài / File I/O:** (Ví dụ: BAI1.INP / BAI1.OUT hoặc cin/cout)
- **Tóm tắt bài toán:**
- **Giới hạn thời gian & bộ nhớ:** (1.0s / 256MB)
- **Ràng buộc dữ liệu chi tiết:**

---

## 2. BẢNG PHÂN TÍCH SUBTASK & ĐỘ PHỨC TẠP
| Subtask / Hướng giải | Điểm số | Giới hạn (N) | Thuật toán đề xuất | Thời gian (O) | Bộ nhớ (O) | Đánh giá |
|---|---|---|---|---|---|---|
| Subtask 1 (Cơ bản / Vét cạn) | 30% | N <= ... | ... | O(...) | O(...) | Ăn chắc 30% điểm |
| Subtask 2 (Cải tiến) | 30% | N <= ... | ... | O(...) | O(...) | Ăn thêm 30% điểm |
| Subtask 3 (Full tối ưu) | 40% | N <= ... | ... | O(...) | O(...) | Đạt 100% điểm |

---

## 3. HƯỚNG GIẢI CHI TIẾT TỪNG SUBTASK
### 🔹 Hướng 1: Thuật toán Cơ bản / Vét cạn (Subtask 1)
- **Ý tưởng:**
- **Đánh giá thời gian thực thi:**

### 🔹 Hướng 2: Thuật toán Cải tiến (Subtask 2)
- **Ý tưởng:**

### 🔹 Hướng 3: Thuật toán Tối ưu Hoàn Hảo (Full 100% Điểm)
- **Ý tưởng cốt lõi & Cấu trúc dữ liệu:**
- **Công thức truy hồi / Thiết kế thuật toán:**
- **Chứng minh tính đúng đắn & Đảm bảo thời gian chạy:**

---

## 4. MÃ NGUỒN C++ (CHUẨN THI ĐẤU FULL ĐIỂM)
```cpp
// Viết code C++ hoàn chỉnh ở đây với Fast I/O và long long
```

---

## 5. MÃ NGUỒN PYTHON 3 (CHUẨN THI ĐẤU FULL ĐIỂM)
```python
# Viết code Python 3 hoàn chỉnh ở đây với sys.stdin.readline
```

---

## 6. PHÂN TÍCH TEST MẪU & BỘ TEST MỞ RỘNG
### 📌 Giải thích Test mẫu trong đề:
- **Input:**
- **Output:**
- **Trace chi tiết từng bước:**

### 📌 Bảng Test Mở Rộng (Corner Cases & Edge Cases):
| STT | Input | Output | Ý nghĩa kiểm thử |
|---|---|---|---|
| 1 | ... | ... | Test biên nhỏ nhất (N=1 hoặc số bé nhất) |
| 2 | ... | ... | Test cực đại (cận trên N, số lớn) |
| 3 | ... | ... | Test trường hợp đặc biệt (số âm, mảng bằng nhau) |
| 4 | ... | ... | Test bẫy tràn số (tổng vượt quá 2*10^9) |

---

## 7. BỘ SINH TEST NGẪU NHIÊN (PYTHON TEST GENERATOR)
```python
# Script Python sinh test ngẫu nhiên phục vụ Stress Test
```

---

## 8. PHẢN BIỆN CHUYÊN GIA & CÁC LỖI THƯỜNG GẶP (COMMON PITFALLS)
- **Bẫy 1:**
- **Bẫy 2:**
- **Lời khuyên khi nộp bài thi:**
"""

class MultiAgentSolver:
    def __init__(self, ollama_client: OllamaClient, cloud_client: Optional[CloudClient] = None):
        self.ollama = ollama_client
        self.cloud = cloud_client

    async def run_agent_pipeline(
        self,
        problem_text: str,
        preferred_model: str = DEFAULT_THINKING_MODEL,
        provider: str = "ollama",
        temperature: float = 0.2
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Chạy quy trình Đa Agent (hỗ trợ cả Ollama và Cloud AI với xoay vòng key):
        """
        yield {
            "type": "agent_step",
            "step_index": 0,
            "step": AGENT_STEPS[0],
            "status": "active",
            "message": f"Agent 1 (ConstraintAnalyst) đang thẩm định ràng buộc bằng [{provider.upper()}]..."
        }

        formatted_prompt = PROMPT_MULTI_AGENT_SYNTHESIS.replace("{problem_text}", problem_text)
        system_inst = "Bạn là Đội đồng Chuyên gia Huấn luyện Học Sinh Giỏi Tin Học Quốc Gia."

        token_count = 0
        step_thresholds = [200, 500, 1000, 1500]
        current_step_idx = 0

        # Chọn generator tương ứng theo provider
        if provider == "gemini" and self.cloud:
            stream_gen = self.cloud.stream_gemini(
                prompt=formatted_prompt,
                system_prompt=system_inst,
                model=preferred_model if "gemini" in preferred_model else "gemini-3.6-flash",
                temperature=temperature
            )
        elif provider == "deepseek" and self.cloud:
            stream_gen = self.cloud.stream_openai_compatible(
                prompt=formatted_prompt,
                system_prompt=system_inst,
                model=preferred_model if "deepseek" in preferred_model else "deepseek-chat",
                provider="deepseek",
                temperature=temperature
            )
        else:
            # Mặc định dùng Ollama
            stream_gen = self.ollama.stream_generate(
                prompt=formatted_prompt,
                system=system_inst,
                model=preferred_model,
                temperature=temperature
            )

        async for token in stream_gen:
            token_count += 1
            yield {"type": "token", "content": token}

            if current_step_idx < len(step_thresholds) and token_count >= step_thresholds[current_step_idx]:
                yield {
                    "type": "agent_step",
                    "step_index": current_step_idx,
                    "step": AGENT_STEPS[current_step_idx],
                    "status": "completed",
                    "message": f"Hoàn thành: {AGENT_STEPS[current_step_idx]['name']}"
                }
                current_step_idx += 1
                if current_step_idx < len(AGENT_STEPS):
                    yield {
                        "type": "agent_step",
                        "step_index": current_step_idx,
                        "step": AGENT_STEPS[current_step_idx],
                        "status": "active",
                        "message": f"{AGENT_STEPS[current_step_idx]['agent']} đang thực hiện: {AGENT_STEPS[current_step_idx]['name']}..."
                    }

        for i in range(current_step_idx, len(AGENT_STEPS)):
            yield {
                "type": "agent_step",
                "step_index": i,
                "step": AGENT_STEPS[i],
                "status": "completed",
                "message": f"Hoàn tất: {AGENT_STEPS[i]['name']}"
            }

        yield {"type": "done"}
