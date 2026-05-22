import os
import json
import random
import requests
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
GEOJSON_URL = "https://raw.githubusercontent.com/evansd/uk-ceremonial-counties/master/uk-ceremonial-counties.geojson"
GEOJSON_PATH = os.path.join(DATA_DIR, 'uk_counties.geojson')

def download_geojson():
    """Tải GeoJSON với cơ chế caching và error handling."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Cơ chế caching: Nếu file đã tồn tại thì bỏ qua tải
    if os.path.exists(GEOJSON_PATH):
        print(f"File {GEOJSON_PATH} đã tồn tại. Bỏ qua tải.")
        return GEOJSON_PATH

    print(f"Đang tải GeoJSON từ {GEOJSON_URL}...")
    try:
        response = requests.get(GEOJSON_URL, timeout=30)
        response.raise_for_status() # Sinh lỗi nếu HTTP status code không phải 200
        
        with open(GEOJSON_PATH, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Tải file GeoJSON thành công!")
        return GEOJSON_PATH
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi tải GeoJSON: {e}")
        return None

def extract_regions_from_geojson(filepath):
    """Trích xuất danh sách county hợp lệ từ file GeoJSON UK ceremonial counties."""
    region_list = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for feature in data.get('features', []):
                region_name = feature.get('properties', {}).get('county')
                if region_name:
                    region_list.append(region_name)
    except Exception as e:
        print(f"Lỗi đọc GeoJSON: {e}")
    return region_list

def generate_covid_cases(region_list, start_date, end_date):
    """Tạo dữ liệu COVID-19 giả lập."""
    print("Đang tạo covid_confirmed_uk.csv...")
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    for region in tqdm(region_list, desc="Generating cases"):
        row = {
            "county_name": region,
            "Country": "UK"
        }
        
        # Tạo cumulative cases (ca bệnh cộng dồn luôn tăng dần)
        cumulative = random.randint(100, 1000)
        for d in date_range:
            date_str = d.strftime('%Y-%m-%d')
            # 30% khả năng tăng ca mới
            if random.random() < 0.3:
                cumulative += random.randint(1, 50)
            row[date_str] = cumulative
            
        data.append(row)
        
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(DATA_DIR, 'covid_confirmed_uk.csv'), index=False)
    print("Đã tạo xong covid_confirmed_uk.csv")

def generate_covid_population(region_list):
    """Tạo dữ liệu dân số giả lập."""
    print("Đang tạo covid_uk_population.csv...")
    data = []
    for region in tqdm(region_list, desc="Generating population"):
        row = {
            "county_name": region,
            "Country": "UK",
            "population": random.randint(10000, 1000000)
        }
        data.append(row)
        
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(DATA_DIR, 'covid_uk_population.csv'), index=False)
    print("Đã tạo xong covid_uk_population.csv")


if __name__ == "__main__":
    geojson_path = download_geojson()
    if not geojson_path:
        print("Không thể tiếp tục do không tải được GeoJSON.")
        exit(1)
        
    region_list = extract_regions_from_geojson(geojson_path)
    if not region_list:
        print("Không tìm thấy region (county) nào trong GeoJSON.")
        exit(1)
        
    # Tạo dữ liệu cho tất cả các counties
    sample_regions = region_list
    
    START_DATE = '2020-03-01'
    END_DATE = '2020-12-31'
    
    generate_covid_cases(region_list, START_DATE, END_DATE)
    generate_covid_population(region_list)
    
    print("HOÀN THÀNH tạo dữ liệu mẫu cho UK!")
