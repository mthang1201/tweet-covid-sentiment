import os
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')

def load_and_filter_tweets(filepath):
    print(f"Đang tải dữ liệu từ {filepath}...")
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Không tìm thấy file {filepath}. Vui lòng chạy script 00_generate_sample_data.py trước.")
        return None

    initial_count = len(df)
    
    # 1. Bỏ retweet (chú ý kiểu dữ liệu có thể là string 'true' hoặc bool True)
    df = df[~df['is_retweet'].astype(str).str.lower().isin(['true', '1', 'yes'])]
    
    # 2. Chỉ giữ user_type = person
    if 'user_type' in df.columns:
        df = df[df['user_type'].astype(str).str.lower() == 'person']
        
    # 3. Chỉ giữ tweet có county_fips
    df = df.dropna(subset=['county_fips'])
    
    # Chuẩn hóa county_fips thành integer rồi thành string độ dài 5 (để match chuẩn FIPS)
    df['county_fips'] = df['county_fips'].astype(int).astype(str).str.zfill(5)
    
    # 4. Parse `created_at` thành date (loại bỏ nhiễu múi giờ)
    # Dùng utc=True để parse tất cả các múi giờ về UTC chuẩn, sau đó ép kiểu timezone-naive nếu cần
    df['created_at'] = pd.to_datetime(df['created_at'], utc=True, format='mixed', errors='coerce')
    
    # Loại bỏ các dòng không parse được ngày giờ
    df = df.dropna(subset=['created_at'])
    
    # Lấy ngày (date) chuẩn theo UTC
    df['date'] = df['created_at'].dt.date
    
    filtered_count = len(df)
    print(f"Lọc tweet: {initial_count} -> {filtered_count} tweets.")
    
    return df

def compute_sentiment(df):
    print("Đang tính toán sentiment bằng VADER...")
    analyzer = SentimentIntensityAnalyzer()
    
    def get_vader_score(text):
        if not isinstance(text, str):
            return 0.0
        return analyzer.polarity_scores(text)['compound']
        
    df['sentiment_score'] = df['text'].apply(get_vader_score)
    return df

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tweets_file = os.path.join(DATA_DIR, 'tweets.csv')
    
    df_tweets = load_and_filter_tweets(tweets_file)
    
    if df_tweets is not None and not df_tweets.empty:
        df_sentiment = compute_sentiment(df_tweets)
        
        output_file = os.path.join(OUTPUT_DIR, 'tweets_with_sentiment.csv')
        df_sentiment.to_csv(output_file, index=False)
        print(f"Đã lưu kết quả sentiment vào {output_file}")
    else:
        print("Không có dữ liệu tweet hợp lệ sau khi lọc.")
