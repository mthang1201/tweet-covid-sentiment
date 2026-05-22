import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')

def load_and_prepare_cases():
    cases_file = os.path.join(DATA_DIR, 'covid_confirmed_uk.csv')
    pop_file = os.path.join(DATA_DIR, 'covid_uk_population.csv')
    
    try:
        df_cases = pd.read_csv(cases_file)
        df_pop = pd.read_csv(pop_file)
    except FileNotFoundError as e:
        print(f"Lỗi: {e}. Vui lòng chạy 00_generate_sample_data.py trước để tạo dữ liệu UK giả lập.")
        return None
        
    print("Đang xử lý dữ liệu ca bệnh UK...")
    
    # Identify identifier columns and date columns
    id_vars = ['county_name', 'Country']
    actual_id_vars = [col for col in id_vars if col in df_cases.columns]
    date_cols = [col for col in df_cases.columns if col not in actual_id_vars]
    
    # Melt từ dạng wide (nhiều cột ngày) sang dạng long (cột ngày, cột cases)
    df_melt = pd.melt(df_cases, id_vars=actual_id_vars, value_vars=date_cols, var_name='date', value_name='cumulative_cases')
    
    # Parse date (ISO 8601 YYYY-MM-DD)
    df_melt['date'] = pd.to_datetime(df_melt['date'], errors='coerce')
    df_melt = df_melt.dropna(subset=['date'])
    
    # Sort để tính ca mắc theo ngày
    df_melt = df_melt.sort_values(['county_name', 'date'])
    
    # Tính ca nhiễm mới mỗi ngày (daily incident cases)
    df_melt['daily_cases'] = df_melt.groupby('county_name')['cumulative_cases'].diff().fillna(0)
    # Loại bỏ các giá trị âm (do lỗi dữ liệu hoặc điều chỉnh)
    df_melt['daily_cases'] = df_melt['daily_cases'].clip(lower=0)
    
    # Map population
    pop_dict = df_pop.set_index('county_name')['population'].to_dict()
    df_melt['population'] = df_melt['county_name'].map(pop_dict)
    
    df_melt = df_melt.dropna(subset=['population'])
    df_melt = df_melt[df_melt['population'] > 0]
    
    # Tính cases per 100k
    df_melt['cases_per_100k'] = (df_melt['daily_cases'] / df_melt['population']) * 100000
    
    # Tính rolling average 7 ngày
    df_melt['cases_per_100k_7day_avg'] = df_melt.groupby('county_name')['cases_per_100k'].transform(lambda x: x.rolling(7, min_periods=1).mean())
    
    print("Hoàn thành xử lý dữ liệu ca bệnh.")
    return df_melt

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df_processed = load_and_prepare_cases()
    
    if df_processed is not None:
        output_file = os.path.join(OUTPUT_DIR, 'covid_cases_processed.csv')
        # Format ngày thành string
        df_processed['date'] = df_processed['date'].dt.strftime('%Y-%m-%d')
        df_processed.to_csv(output_file, index=False)
        print(f"Đã lưu kết quả cases vào {output_file}")

