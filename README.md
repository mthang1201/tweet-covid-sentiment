# Tweet Sentiment & COVID-19 Disease Detection

Tái tạo pipeline và kết quả nghiên cứu bài báo "Towards using Tweet sentiment for infectious disease detection" (PLOS ONE, 2025).

## Yêu cầu hệ thống
- Python 3.9+
- Khuyên dùng môi trường ảo (virtual environment)

## Cài đặt
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# MacOS/Linux
source venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt
```

## Cách chạy

### 1. Tạo dữ liệu giả lập (Mock data)
Nếu bạn chưa có dữ liệu thật (tweets, USAFacts), chạy script này để tạo mẫu dữ liệu. Script cũng sẽ tự động tải file geojson các county của Mỹ có cơ chế caching.
```bash
python src/00_generate_sample_data.py
```

### 2. Tính điểm Sentiment
```bash
python src/01_compute_sentiment.py
```

### 3. Tiền xử lý dữ liệu ca bệnh (COVID Cases)
```bash
python src/02_prepare_cases.py
```

### 4. Gộp dữ liệu Sentiment và Cases
Bạn có thể chọn group dữ liệu theo ngày (`daily`) hoặc tuần (`weekly`). Tuần sẽ bắt đầu từ thứ Hai.
```bash
python src/03_merge_data.py --agg-level daily
# hoặc
python src/03_merge_data.py --agg-level weekly
```

### 5. Tính toán Correlation
Tính toán Pearson correlation (Global, Temporal, Spatial, Spatiotemporal).
```bash
python src/04_correlation.py --agg-level daily
```

### 6. Vẽ biểu đồ Temporal Correlation
```bash
python src/05_plot_temporal.py
```

### 7. Vẽ bản đồ Spatial Correlation
```bash
python src/06_plot_map.py
```

Tất cả kết quả sẽ được lưu vào thư mục `outputs/`.
