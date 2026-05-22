import os
import glob
import pandas as pd
from tqdm import tqdm

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')

def process_uk_tweets():
    print("Đang xử lý dữ liệu TSV của UK...")
    tsv_files = glob.glob(os.path.join(DATA_DIR, 'united_kingdom_*.tsv'))
    
    if not tsv_files:
        print("Không tìm thấy file united_kingdom_*.tsv nào trong thư mục data.")
        return
        
    output_file = os.path.join(OUTPUT_DIR, 'tweets_with_sentiment.csv')
    
    # Xóa file output cũ nếu tồn tại
    if os.path.exists(output_file):
        os.remove(output_file)
        
    total_processed = 0
    total_kept = 0
    
    columns_to_read = [
        'tweet_id', 'date_time', 'retweeted_id', 'user_type', 
        'sentiment_label', 'geo_county', 'place_county', 'user_loc_county'
    ]
    
    first_chunk = True
    
    for filepath in sorted(tsv_files):
        print(f"Đang đọc file: {os.path.basename(filepath)}")
        
        # Đọc theo chunk để tránh OOM
        try:
            chunk_iter = pd.read_csv(
                filepath, 
                sep='\t', 
                chunksize=100000, 
                usecols=columns_to_read,
                dtype={'retweeted_id': str} # Để dễ check null
            )
        except Exception as e:
            print(f"Lỗi đọc file {filepath}: {e}")
            continue
            
        for chunk in tqdm(chunk_iter, desc=f"Processing {os.path.basename(filepath)}"):
            total_processed += len(chunk)
            
            # 1. Bỏ retweet (nếu retweeted_id có giá trị tức là retweet)
            chunk = chunk[chunk['retweeted_id'].isna()]
            
            # 2. Chỉ giữ user_type = PER (person)
            if 'user_type' in chunk.columns:
                chunk = chunk[chunk['user_type'].astype(str).str.upper() == 'PER']
                
            # 3. Lấy county name (ưu tiên geo_county -> place_county -> user_loc_county)
            chunk['county_name'] = chunk['geo_county'].fillna(chunk['place_county']).fillna(chunk['user_loc_county'])
            chunk = chunk.dropna(subset=['county_name'])
            chunk = chunk[chunk['county_name'] != 'UNK']
            
            # 4. Parse ngày
            chunk['date_time'] = pd.to_datetime(chunk['date_time'], errors='coerce')
            chunk = chunk.dropna(subset=['date_time'])
            chunk['date'] = chunk['date_time'].dt.date
            
            # 5. Lấy sentiment
            # sentiment_label đã có sẵn (-1, 0, 1), ta dùng nó làm sentiment_score
            chunk['sentiment_score'] = chunk['sentiment_label']
            
            # Giữ lại các cột cần thiết
            final_chunk = chunk[['tweet_id', 'date', 'county_name', 'sentiment_score']]
            total_kept += len(final_chunk)
            
            # Ghi ra file
            final_chunk.to_csv(output_file, mode='a', index=False, header=first_chunk)
            first_chunk = False
            
    print(f"Xử lý hoàn tất. Tổng số tweet đã đọc: {total_processed}. Tổng số tweet hợp lệ giữ lại: {total_kept}.")
    print(f"Đã lưu kết quả vào {output_file}")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    process_uk_tweets()

