import os
import json
import random
import requests
import pandas as pd
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
GEOJSON_URL = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
GEOJSON_PATH = os.path.join(DATA_DIR, 'counties.geojson')

def download_geojson():
    """Tải GeoJSON với cơ chế caching và error handling."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Cơ chế caching: Nếu file đã tồn tại thì bỏ qua tải
    if os.path.exists(GEOJSON_PATH):
        print(f"File {GEOJSON_PATH} đã tồn tại. Bỏ qua tải.")
        return GEOJSON_PATH

    print(f"Đang tải GeoJSON từ {GEOJSON_URL}...")
    try:
        response = requests.get(GEOJSON_URL, timeout=10)
        response.raise_for_status() # Sinh lỗi nếu HTTP status code không phải 200
        
        with open(GEOJSON_PATH, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Tải file GeoJSON thành công!")
        return GEOJSON_PATH
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi tải GeoJSON: {e}")
        # Không dùng sys.exit, trả về None để xử lý phía sau nếu cần
        return None

def extract_fips_from_geojson(filepath):
    """Trích xuất danh sách FIPS hợp lệ từ file GeoJSON."""
    fips_list = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for feature in data.get('features', []):
                fips = feature.get('id')
                if fips:
                    fips_list.append(str(fips).zfill(5))
    except Exception as e:
        print(f"Lỗi đọc GeoJSON: {e}")
    return fips_list

def generate_covid_cases(fips_list, start_date, end_date):
    """Tạo dữ liệu COVID-19 giả lập."""
    print("Đang tạo covid_confirmed_usafacts.csv...")
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    for fips in fips_list:
        county_name = f"County {fips}"
        state_name = "State"
        statefips = fips[:2]
        
        row = {
            "countyFIPS": int(fips),
            "County Name": county_name,
            "State": state_name,
            "StateFIPS": int(statefips)
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
    df.to_csv(os.path.join(DATA_DIR, 'covid_confirmed_usafacts.csv'), index=False)
    print("Đã tạo xong covid_confirmed_usafacts.csv")

def generate_covid_population(fips_list):
    """Tạo dữ liệu dân số giả lập."""
    print("Đang tạo covid_county_population_usafacts.csv...")
    data = []
    for fips in fips_list:
        county_name = f"County {fips}"
        state_name = "State"
        
        row = {
            "countyFIPS": int(fips),
            "County Name": county_name,
            "State": state_name,
            "population": random.randint(10000, 1000000)
        }
        data.append(row)
        
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(DATA_DIR, 'covid_county_population_usafacts.csv'), index=False)
    print("Đã tạo xong covid_county_population_usafacts.csv")

def generate_tweets(fips_list, start_date, end_date, num_tweets=5000):
    """Tạo dữ liệu tweet giả lập có nhiễu thời gian."""
    print("Đang tạo tweets.csv...")
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)
    delta = end_dt - start_dt
    
    # Một số format thời gian có nhiễu để test pipeline
    time_formats = [
        "%Y-%m-%d %H:%M:%S",          # Không có timezone (naive)
        "%Y-%m-%dT%H:%M:%S%z",        # Có timezone UTC (VD: +0000)
        "%Y-%m-%d %H:%M:%S%z",        # Có timezone khác (VD: -0500)
        "%Y-%m-%dT%H:%M:%SZ"          # ISO format UTC (Z)
    ]
    
    timezones = ["+0000", "-0500", "-0800", "+0700"]
    
    sample_texts = [
        "covid is getting worse here",
        "finally recovered from covid",
        "wearing masks is important",
        "i hate lockdown",
        "cases are dropping, great news!",
        "hospital is full, very sad.",
        "vaccine is working well",
        "this pandemic will never end"
    ]
    
    data = []
    for i in range(1, num_tweets + 1):
        # Random thời gian trong khoảng start - end
        random_seconds = random.randint(0, int(delta.total_seconds()))
        tweet_dt = start_dt + timedelta(seconds=random_seconds)
        
        fmt = random.choice(time_formats)
        tz = random.choice(timezones)
        
        if '%z' in fmt:
            created_at = tweet_dt.strftime(fmt.replace('%z', tz))
        elif 'Z' in fmt:
            created_at = tweet_dt.strftime(fmt)
        else:
            created_at = tweet_dt.strftime(fmt)
            
        row = {
            "tweet_id": i,
            "created_at": created_at,
            "text": random.choice(sample_texts),
            "county_fips": int(random.choice(fips_list)),
            "is_retweet": random.choice(["true", "false", "false", "false"]), # 25% là retweet
            "user_type": random.choice(["person", "person", "organization", "bot"])
        }
        data.append(row)
        
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(DATA_DIR, 'tweets.csv'), index=False)
    print("Đã tạo xong tweets.csv")

if __name__ == "__main__":
    geojson_path = download_geojson()
    if not geojson_path:
        print("Không thể tiếp tục do không tải được GeoJSON.")
        exit(1)
        
    fips_list = extract_fips_from_geojson(geojson_path)
    if not fips_list:
        print("Không tìm thấy mã FIPS nào trong GeoJSON.")
        exit(1)
        
    # Giới hạn số lượng FIPS để tạo dữ liệu nhanh hơn (lấy 100 county ngẫu nhiên)
    sample_fips = random.sample(fips_list, min(100, len(fips_list)))
    
    START_DATE = '2020-03-01'
    END_DATE = '2020-12-31'
    
    generate_covid_cases(sample_fips, START_DATE, END_DATE)
    generate_covid_population(sample_fips)
    generate_tweets(sample_fips, START_DATE, END_DATE, num_tweets=10000)
    
    print("HOÀN THÀNH tạo dữ liệu mẫu!")
