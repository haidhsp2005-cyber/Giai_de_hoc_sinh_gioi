# HSG SOLVER AI - TRỢ LÝ GIẢI ĐỀ THI HỌC SINH GIỎI TIN HỌC 🏆

Ứng dụng web chuyên sâu hỗ trợ học sinh và giáo viên giải đề thi Học Sinh Giỏi (HSG) / Olympic Tin học (VNOI, HSG Tỉnh, HSG Quốc Gia). 
Hệ thống sử dụng các mô hình AI chạy cục bộ qua **Ollama** (ưu tiên **`qwen2.5:7b`** và **`qwen2.5-coder:7b`**), hỗ trợ đọc tài liệu từ file Word (`.docx`), PDF (`.pdf`), hình ảnh chụp đề thi hoặc dán trực tiếp.

---

## 🚀 Tính năng nổi bật

1. **Đọc đa định dạng tài liệu**:
   - File Word (`.docx`): Bóc tách tiêu đề, đoạn văn và các bảng biểu (bảng subtask, bảng test ví dụ).
   - File PDF (`.pdf`): Trích xuất văn bản số từ các trang.
   - Hình ảnh chụp đề (`.png`, `.jpg`, `.jpeg`): Tích hợp OCR nhận diện văn bản.
   - Hỗ trợ phím tắt **Ctrl + V** để dán ảnh chụp màn hình trực tiếp từ clipboard.

2. **Phân tích đề bài & Subtasks chuẩn HSG**:
   - Tóm tắt bản chất bài toán, phân tích giới hạn thời gian (Time Limit) và bộ nhớ (Memory Limit).
   - Bảng phân tích chi tiết từng Subtask (điểm số, giới hạn dữ liệu $N$, thuật toán yêu cầu, độ phức tạp thời gian & bộ nhớ).
   - **Tự động phân cấp nếu đề không có subtask**:
     - *Hướng 1 (Cơ bản / Vét cạn / Brute-force)*: Lấy 30-40% điểm ban đầu.
     - *Hướng 2 (Cải tiến / Trung bình)*: Tối ưu một phần.
     - *Hướng 3 (Tối ưu / Full điểm 100%)*: Thuật toán chuẩn đạt điểm tối đa.

3. **Cung cấp mã nguồn 2 ngôn ngữ**:
   - **C++ (C++17/20)**: Fast I/O (`cin.tie(NULL)`), cấu trúc hàm rõ ràng, chống tràn số (`long long`), chú thích tiếng Việt chi tiết, hỗ trợ cả `freopen` cho file `*.INP` và `*.OUT`.
   - **Python 3**: Tối ưu I/O bằng `sys.stdin.readline`, mở rộng độ sâu đệ quy `sys.setrecursionlimit(10**6)`, phong cách lập trình pythonic.

4. **Sinh Test mẫu & Test Generator**:
   - Giải thích chi tiết từng bước tính toán của Test mẫu trong đề bài.
   - Sinh các bộ Test mở rộng (Corner cases: $N=1, N=0$, cực trị âm/dương, mảng phần tử bằng nhau).
   - Cung cấp mã nguồn Python script sinh test ngẫu nhiên (`test_gen.py`) phục vụ Stress Test so sánh giữa code Trâu và code Full điểm.

5. **Giao diện Web Competitive Programming hiện đại**:
   - Chế độ Sáng / Tối (Dark / Light Mode).
   - Hiển thị công thức toán học $O(N \log N)$ sắc nét bằng **KaTeX**.
   - Syntax Highlighting bằng **Prism.js**.
   - Nút **Sao chép 1-Click** và **Tải file** (`solution.cpp`, `solution.py`, `test_gen.py`).
   - Tự động quét và hiển thị toàn bộ mô hình đang có trong Ollama máy tính.

---

## 💻 Cách khởi chạy ứng dụng

### Cách 1: Chạy bằng file `run.bat` (Khuyên dùng)
Nhấp đúp chuột vào file `run.bat` trong thư mục `hsg_solver`. Hệ thống sẽ tự động kiểm tra kết nối Ollama và mở trình duyệt web tại địa chỉ:
👉 **http://127.0.0.1:8000**

### Cách 2: Chạy bằng dòng lệnh (Terminal / PowerShell)
```bash
cd C:\Users\Admin\.gemini\antigravity\scratch\hsg_solver
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Sau đó mở trình duyệt và truy cập: **http://127.0.0.1:8000**

---

## 📁 Cấu trúc thư mục

```
hsg_solver/
├── app.py                  # Server FastAPI xử lý API, SSE streaming và định tuyến
├── config.py               # Cấu hình Ollama URL, default models, thư mục uploads
├── document_parser.py      # Module đọc file .docx, .pdf, hình ảnh OCR
├── prompt_templates.py     # System prompt chuyên sâu cho HSG Tin Học và Subtasks
├── ollama_client.py        # Client kết nối Ollama (hỗ trợ streaming thời gian thực)
├── run.bat                 # Script 1-click khởi động ứng dụng
├── requirements.txt        # Danh sách thư viện Python
├── templates/
│   └── index.html          # Giao diện chính Responsive, tích hợp KaTeX, Prism.js
├── static/
│   ├── css/style.css       # Giao diện lập trình viên hiện đại (Dark/Light mode)
│   └── js/app.js           # Xử lý kéo thả, upload, streaming, copy/download code
└── uploads/                # Thư mục lưu trữ tạm các file đề bài tải lên
```
