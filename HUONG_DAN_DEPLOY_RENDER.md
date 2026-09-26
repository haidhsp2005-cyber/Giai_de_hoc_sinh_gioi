# 🚀 HƯỚNG DẪN ĐƯA TRANG WEB HSG SOLVER AI LÊN RENDER (MIỄN PHÍ 100%)

Tài liệu này hướng dẫn chi tiết từng bước để đưa trang web **HSG Solver AI** lên nền tảng đám mây **Render.com** để có thể truy cập trực tuyến từ bất kỳ điện thoại, máy tính nào qua internet với tên miền miễn phí dạng `https://ten-du-an.onrender.com`.

---

## 📌 TỔNG QUAN CÁC BƯỚC THỰC HIỆN

Quy trình chuẩn gồm 3 bước đơn giản:
1. **Bước 1**: Đưa mã nguồn lên GitHub (Đã chuẩn bị sẵn script tự động).
2. **Bước 2**: Kết nối GitHub với Render.com và tạo Web Service.
3. **Bước 3**: Điền danh sách API Key Gemini vào Biến môi trường (Environment Variables) trên Render.

---

## 🛠️ BƯỚC 1: ĐẨY MÃ NGUỒN LÊN GITHUB

Mã nguồn dự án tại máy bạn đã được khởi tạo Git sẵn sàng. Bây giờ bạn chỉ cần tạo 1 Repository trên GitHub:

1. Mở trình duyệt vào: 👉 **[https://github.com/new](https://github.com/new)** (Đăng nhập GitHub).
2. Tại ô **Repository name**: Đặt tên bất kỳ, ví dụ: `hsg-solver-ai`.
3. Bạn có thể chọn **Public** (Công khai) hoặc **Private** (Riêng tư - khuyên dùng).
   > **Lưu ý**: *Không* tích chọn "Add a README file" hay .gitignore (vì trong máy đã có sẵn).
4. Nhấn **Create repository**.
5. Copy đường dẫn HTTPS của repo vừa tạo, ví dụ:
   `https://github.com/your-username/hsg-solver-ai.git`
6. Tại thư mục dự án trên máy tính:
   - Nhấp đúp vào tệp: [**`push_to_github.bat`**](file:///C:/Users/Admin/.gemini/antigravity/scratch/hsg_solver/push_to_github.bat)
   - Dán đường dẫn repo GitHub bạn vừa copy vào và nhấn **Enter**.
   - Toàn bộ mã nguồn sẽ tự động được đồng bộ lên GitHub trong vài giây!

*(Nếu thích gõ lệnh trong Terminal, bạn chỉ cần chạy:)*
```bash
git remote add origin https://github.com/your-username/hsg-solver-ai.git
git branch -M main
git push -u origin main
```

---

## 🌐 BƯỚC 2: TRIỂN KHAI TRÊN RENDER.COM

1. Truy cập vào trang quản trị: 👉 **[https://dashboard.render.com](https://dashboard.render.com)**
2. Đăng nhập bằng tài khoản **GitHub** của bạn.
3. Ở góc trên bên phải, nhấn nút **`New +`** $\to$ Chọn **`Web Service`**.
4. Chọn tuỳ chọn **"Build and deploy from a Git repository"** $\to$ Bấm **Next**.
5. Trong danh sách repositories, tìm `hsg-solver-ai` $\to$ Bấm **`Connect`**.

---

## ⚙️ BƯỚC 3: CẤU HÌNH THÔNG SỐ TRÊN RENDER

Render sẽ yêu cầu nhập các thông tin sau:

| Mục | Giá trị cần điền | Ghi chú |
| :--- | :--- | :--- |
| **Name** | `hsg-solver-ai` | Tên trang web của bạn trên link `.onrender.com` |
| **Region** | `Singapore` | Gần Việt Nam nhất, tốc độ tải nhanh nhất |
| **Branch** | `main` | Nhánh chính của mã nguồn |
| **Runtime** | `Python 3` | Ngôn ngữ hệ thống |
| **Build Command** | `pip install -r requirements.txt` | Cài đặt các thư viện tự động |
| **Start Command** | `uvicorn app:app --host 0.0.0.0 --port $PORT` | Lệnh khởi động server |
| **Instance Type** | `Free` ($0/month) | Miễn phí hoàn toàn |

*(Gợi ý: Do dự án đã có sẵn file `render.yaml`, Render có thể tự động điền sẵn các thông số này cho bạn).*

---

## 🔑 BƯỚC 4: CẤU HÌNH API KEYS TRÊN RENDER (BẢO MẬT TUYỆT ĐỐI)

Do file `.env` chứa các API Key riêng tư của bạn đã được chặn (không đẩy lên GitHub công khai để đảm bảo an toàn), bạn cần điền các key này trực tiếp vào Render:

1. Cuộn xuống mục **Environment Variables** (Biến môi trường) trên trang cấu hình của Render.
2. Bấm nút **Add Environment Variable** để thêm biến:

### Cách 1 (Khuyên dùng - Nhanh gọn nhất):
- **Key**: `GEMINI_API_KEYS`
- **Value**: Dán toàn bộ các API Key của bạn ngăn cách nhau bằng dấu phẩy:
  ```
  AQ.Ab8RN6IIIDHqy...,AQ.Ab8RN6LGCEuT...,AQ.Ab8RN6LSmIvH...
  ```

### Cách 2: Từng dòng một:
- `GEMINI_API_KEY_1` = `AQ.Ab8RN6IIIDHqy...`
- `GEMINI_API_KEY_2` = `AQ.Ab8RN6LGCEuT...`
- `GEMINI_API_KEY_3` = `AQ.Ab8RN6LSmIvH...`
- (Thêm tiếp các key nếu bạn có)

3. Thêm biến chọn Model mặc định:
- **Key**: `DEFAULT_GEMINI_MODEL`
- **Value**: `gemini-flash-latest`

---

## 🎉 BƯỚC 5: BẤM DEPLOY VÀ HƯỞNG THÀNH QUẢ

1. Nhấn nút màu tím: **`Deploy Web Service`** (hoặc `Create Web Service`).
2. Màn hình Render sẽ hiển thị dòng log cài đặt:
   ```
   ==> Installing dependencies...
   ==> Running 'uvicorn app:app --host 0.0.0.0 --port $PORT'
   ==> Your service is live 🎉
   ```
3. Sau 1 - 2 phút, ở góc trên bên trái dưới tên dự án sẽ xuất hiện đường link công khai, ví dụ:
   👉 **`https://hsg-solver-ai.onrender.com`**

Bạn có thể bấm vào đường link này, gửi cho bạn bè, học sinh hoặc mở trên điện thoại để giải đề thi HSG ở bất kỳ đâu!

---

## 💡 CÁC ĐIỂM CẦN LƯU Ý KHI CHẠY TRÊN RENDER:
1. **Ollama Local trên đám mây**: Do Render Free không có GPU cục bộ để chạy Ollama, hệ thống đám mây sẽ sử dụng **Google Gemini Online** làm công cụ giải chính. Hệ thống tự động xoay vòng danh sách các API Key bạn đã nạp, đảm bảo giải đề cực nhanh và không bao giờ bị nghẽn!
2. **Nhận diện Ảnh Đề Bài (OCR)**: Dự án đã được tích hợp sẵn công nghệ **Gemini Multimodal Vision**. Khi bạn tải ảnh đề bài lên Render, AI của Gemini sẽ tự động bóc tách chữ, công thức toán và bảng biểu chính xác 100%!
3. **Gói Free của Render**: Máy chủ gói Free sẽ tự động vào chế độ "ngủ" (Sleep) nếu không có ai truy cập trong 15 phút. Lần truy cập đầu tiên sau khi ngủ sẽ mất khoảng 30 - 45 giây để máy chủ khởi động lại, sau đó sẽ hoạt động bình thường mượt mà.
