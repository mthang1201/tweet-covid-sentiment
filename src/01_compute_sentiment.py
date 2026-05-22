import os
import glob
import pandas as pd
from tqdm import tqdm

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')

def process_uk_tweets():
    print("Processing UK tweet TSV data...")
    tsv_files = sorted(glob.glob(os.path.join(DATA_DIR, 'united_kingdom_*.tsv')))
    
    if not tsv_files:
        print("No united_kingdom_*.tsv files found in data directory.")
        return
    
    print(f"Found {len(tsv_files)} TSV files to process.")
        
    output_file = os.path.join(OUTPUT_DIR, 'tweets_with_sentiment.csv')
    
    # Remove old output if exists
    if os.path.exists(output_file):
        os.remove(output_file)
        
    total_processed = 0
    total_kept = 0
    
    # Only read the columns we need to save memory
    columns_to_read = [
        'tweet_id', 'date_time', 'retweeted_id', 'user_type', 
        'sentiment_label', 'geo_county', 'place_county', 'user_loc_county'
    ]
    
    first_chunk = True
    
    for file_idx, filepath in enumerate(tsv_files, start=1):
        print(f"\n[{file_idx}/{len(tsv_files)}] Reading file: {os.path.basename(filepath)}")
        
        # Read in chunks to avoid OOM with large files
        try:
            chunk_iter = pd.read_csv(
                filepath, 
                sep='\t', 
                chunksize=100000, 
                usecols=columns_to_read,
                dtype={'retweeted_id': str},  # To easily check null
                on_bad_lines='skip',
                low_memory=False
            )
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            continue
            
        for chunk in tqdm(chunk_iter, desc=f"Processing {os.path.basename(filepath)}"):
            total_processed += len(chunk)
            
            # 1. Remove retweets (if retweeted_id has a value, it's a retweet)
            chunk = chunk[chunk['retweeted_id'].isna()]
            
            # 2. Keep only user_type = PER (person)
            if 'user_type' in chunk.columns:
                chunk = chunk[chunk['user_type'].astype(str).str.upper() == 'PER']
                
            # 3. Resolve county name (priority: geo_county -> place_county -> user_loc_county)
            chunk['county_name'] = chunk['geo_county'].fillna(chunk['place_county']).fillna(chunk['user_loc_county'])
            chunk = chunk.dropna(subset=['county_name'])
            chunk = chunk[chunk['county_name'] != 'UNK']
            
            # 4. Parse datetime
            chunk['date_time'] = pd.to_datetime(chunk['date_time'], errors='coerce')
            chunk = chunk.dropna(subset=['date_time'])
            chunk['date'] = chunk['date_time'].dt.date
            
            # 5. Use the pre-computed sentiment_label as sentiment_score
            # sentiment_label is already -1 (negative), 0 (neutral), 1 (positive)
            chunk['sentiment_score'] = chunk['sentiment_label']
            
            # Keep only necessary columns
            final_chunk = chunk[['tweet_id', 'date', 'county_name', 'sentiment_score']]
            total_kept += len(final_chunk)
            
            # Write to output file
            final_chunk.to_csv(output_file, mode='a', index=False, header=first_chunk)
            first_chunk = False
            
    print(f"\nProcessing complete. Total tweets read: {total_processed:,}. Valid tweets kept: {total_kept:,}.")
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    process_uk_tweets()
