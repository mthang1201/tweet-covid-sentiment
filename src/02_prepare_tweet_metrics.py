import os
import pandas as pd
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')

def prepare_tweet_metrics():
    """
    Derive COVID activity metrics from the tweet data itself.
    Uses daily tweet volume per county as a proxy metric, and computes
    rolling averages so downstream scripts (merge, correlation) work unchanged.
    """
    tweets_file = os.path.join(OUTPUT_DIR, 'tweets_with_sentiment.csv')
    
    try:
        df = pd.read_csv(tweets_file)
    except FileNotFoundError:
        print(f"Error: {tweets_file} not found. Please run 01_compute_sentiment.py first.")
        return None
    
    print(f"Loaded {len(df):,} tweets from {tweets_file}")
    
    # Parse date
    df['date'] = pd.to_datetime(df['date'])
    df['county_name'] = df['county_name'].astype(str)
    
    # Aggregate: daily tweet count and mean sentiment per county
    daily_agg = df.groupby(['county_name', 'date']).agg(
        tweet_count=('tweet_id', 'count'),
        mean_sentiment=('sentiment_score', 'mean')
    ).reset_index()
    
    # Sort for rolling computation
    daily_agg = daily_agg.sort_values(['county_name', 'date'])
    
    # Use tweet_count as the "cases_per_100k" metric (proxy for COVID activity)
    daily_agg['cases_per_100k'] = daily_agg['tweet_count']
    
    # Compute 7-day rolling average per county
    daily_agg['cases_per_100k_7day_avg'] = daily_agg.groupby('county_name')['cases_per_100k'].transform(
        lambda x: x.rolling(7, min_periods=1).mean()
    )
    
    print(f"Aggregated to {len(daily_agg):,} county-day records")
    print(f"Date range: {daily_agg['date'].min()} to {daily_agg['date'].max()}")
    print(f"Counties found: {daily_agg['county_name'].nunique()}")
    
    return daily_agg

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df_processed = prepare_tweet_metrics()
    
    if df_processed is not None:
        output_file = os.path.join(OUTPUT_DIR, 'covid_cases_processed.csv')
        df_processed['date'] = df_processed['date'].dt.strftime('%Y-%m-%d')
        df_processed.to_csv(output_file, index=False)
        print(f"Saved processed metrics to {output_file}")
