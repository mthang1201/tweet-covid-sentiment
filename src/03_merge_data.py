import os
import argparse
import pandas as pd

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')

def merge_data(agg_level):
    tweets_file = os.path.join(OUTPUT_DIR, 'tweets_with_sentiment.csv')
    cases_file = os.path.join(OUTPUT_DIR, 'covid_cases_processed.csv')
    
    try:
        df_tweets = pd.read_csv(tweets_file)
        df_cases = pd.read_csv(cases_file)
    except FileNotFoundError as e:
        print(f"Lỗi: {e}. Vui lòng chạy 01_compute_sentiment.py và 02_prepare_cases.py trước.")
        return
        
    print(f"Đang merge dữ liệu với mức độ aggregate: {agg_level}...")
    
    # Ép kiểu date
    df_tweets['date'] = pd.to_datetime(df_tweets['date'])
    df_cases['date'] = pd.to_datetime(df_cases['date'])
    
    # Chuẩn hóa FIPS để merge không bị lỗi
    df_tweets['county_fips'] = df_tweets['county_fips'].astype(str).str.zfill(5)
    df_cases['countyFIPS'] = df_cases['countyFIPS'].astype(str).str.zfill(5)
    
    if agg_level == 'weekly':
        # Group by tuần (bắt đầu từ Thứ Hai: W-MON)
        # Sử dụng pd.Grouper cho time series nếu index là date, hoặc chuyển date thành đầu tuần
        df_tweets['period'] = df_tweets['date'] - pd.to_timedelta(df_tweets['date'].dt.dayofweek, unit='d')
        df_cases['period'] = df_cases['date'] - pd.to_timedelta(df_cases['date'].dt.dayofweek, unit='d')
    else:
        df_tweets['period'] = df_tweets['date']
        df_cases['period'] = df_cases['date']
        
    # Aggregate sentiment
    agg_tweets = df_tweets.groupby(['county_fips', 'period'])['sentiment_score'].mean().reset_index()
    
    # Aggregate cases
    # Với daily, lấy cases_per_100k_7day_avg (trung bình động 7 ngày)
    # Với weekly, lấy trung bình của cases_per_100k trong tuần đó
    agg_cases = df_cases.groupby(['countyFIPS', 'period'])['cases_per_100k'].mean().reset_index()
    agg_cases.rename(columns={'cases_per_100k': 'cases_metric'}, inplace=True)
    
    # Cố gắng lấy thêm cột cases_per_100k_7day_avg nếu là daily
    if agg_level == 'daily':
        agg_cases_7d = df_cases.groupby(['countyFIPS', 'period'])['cases_per_100k_7day_avg'].mean().reset_index()
        agg_cases = pd.merge(agg_cases, agg_cases_7d, on=['countyFIPS', 'period'], how='left')
        agg_cases['cases_metric'] = agg_cases['cases_per_100k_7day_avg'] # Dùng 7-day avg cho daily
        
    # Merge!
    merged_df = pd.merge(
        agg_tweets, 
        agg_cases, 
        left_on=['county_fips', 'period'], 
        right_on=['countyFIPS', 'period'], 
        how='inner' # Chỉ giữ những ngày/tuần và county có cả tweet và ca bệnh
    )
    
    # Dọn dẹp cột
    merged_df.drop(columns=['countyFIPS'], inplace=True)
    
    output_file = os.path.join(OUTPUT_DIR, f'merged_data_{agg_level}.csv')
    merged_df.to_csv(output_file, index=False)
    print(f"Đã lưu kết quả merge vào {output_file} (Số dòng: {len(merged_df)})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge sentiment and cases data.")
    parser.add_argument('--agg-level', choices=['daily', 'weekly'], default='daily', 
                        help="Mức độ aggregate (daily hoặc weekly)")
    args = parser.parse_args()
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    merge_data(args.agg_level)
