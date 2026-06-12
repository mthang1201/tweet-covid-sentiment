# Tweet Sentiment & COVID-19 Disease Detection

Tái tạo pipeline nghiên cứu bài báo "Towards using Tweet sentiment for infectious disease detection" (PLOS ONE, 2025). Hệ thống đi kèm với một **Web Dashboard giao diện cực đẹp** cho phép bạn thao tác, phân tích và xem biểu đồ tương quan trực quan.

## Cấu trúc Hệ thống
- **`src/`**: Chứa các scripts xử lý dữ liệu, phân tích sentiment và vẽ bản đồ.
- **`api/`**: FastAPI backend để kích hoạt các scripts và phục vụ ảnh.
- **`web/`**: Vite + React frontend (Dark mode, Glassmorphism).
- **`demo/`**: Bản dashboard tĩnh dùng để publish trực tiếp lên GitHub Pages.
- **`data/` & `outputs/`**: Nơi chứa raw data và kết quả (ảnh, csv).

## Yêu cầu
- Python 3.9+
- Node.js 18+ (để chạy giao diện Vite)

## Hướng dẫn Khởi chạy (Chỉ 2 bước)

### Bước 1: Khởi động Backend (Python FastAPI)
Mở một terminal mới và chạy:

```bash
# Tạo môi trường ảo (nếu chưa có)
python3 -m venv venv

# Kích hoạt môi trường
# Trên Windows:
venv\Scripts\activate
# Trên MacOS/Linux:
source venv/bin/activate

# Cài đặt thư viện pipeline & backend
pip install -r requirements.txt
pip install -r api_requirements.txt

# Khởi chạy server
python3 api/main.py
```
*Server sẽ chạy ở địa chỉ: `http://localhost:8000`*

### Bước 2: Khởi động Frontend (React)
Mở một terminal **thứ hai** và chạy:

```bash
cd web
npm install
npm run dev
```
*Giao diện sẽ hiển thị ở địa chỉ (thường là): `http://localhost:5173`*

---

## Cách sử dụng Dashboard
1. Truy cập vào giao diện web (`http://localhost:5173`).
2. Chọn mức độ aggregate (Daily hoặc Weekly) ở thanh bên trái.
3. Bấm **"Run Pipeline"**. 
4. Hãy chờ vài phút (có spinner xoay xoay). Quá trình này sẽ ngầm gọi các bước: tạo mock data, parse thời gian, tính toán sentiment, merge cases và vẽ đồ thị.
5. Sau khi kết thúc, điểm **Global Correlation**, biểu đồ **Temporal** và bản đồ **Spatial** (trên lục địa Mỹ) sẽ hiện ra cực kỳ lung linh.

## Publish demo tĩnh lên GitHub Pages
Thư mục **`demo/`** chứa dashboard HTML/CSS/JS tĩnh và các ảnh output hiện tại, không cần backend hoặc Vite dev server. Có thể publish GitHub Pages từ root rồi truy cập `/demo/`, hoặc dùng GitHub Actions để deploy riêng nội dung trong `demo/` làm site root.

Trong bản demo tĩnh, nút **Run Pipeline** không gọi API. Khi bấm nút, trang sẽ yêu cầu người dùng mở GitHub repo, tải dataset từ [TB-COV](https://crisisnlp.qcri.org/tbcov), rồi chạy pipeline thủ công trên máy local để tạo output mới.
