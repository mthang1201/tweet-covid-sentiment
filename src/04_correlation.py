import os
import argparse
import pandas as pd
from scipy.stats import pearsonr

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')

def safe_pearson(x, y):
    """Calculate Pearson correlation safely, handling edge cases."""
    if len(x) < 3:
        return None
    if x.nunique() == 1 or y.nunique() == 1:
        return None
    r, p = pearsonr(x, y)
    return r

def compute_correlations(agg_level):
    merged_file = os.path.join(OUTPUT_DIR, f'merged_data_{agg_level}.csv')
    try:
        df = pd.read_csv(merged_file)
    except FileNotFoundError:
        print(f"File {merged_file} not found. Please run 03_merge_data.py first.")
        return
        
    df['period'] = pd.to_datetime(df['period'])
    
    print("1. Computing Global Correlation...")
    global_corr = safe_pearson(df['sentiment_score'], df['cases_metric'])
    print(f"   => Global Correlation: {global_corr}")
    with open(os.path.join(OUTPUT_DIR, f'global_correlation_{agg_level}.txt'), 'w') as f:
        f.write(f"Global Correlation: {global_corr}\n")
        
    print("2. Computing Temporal Correlation (by time period)...")
    temporal_corr = df.groupby('period').apply(
        lambda g: safe_pearson(g['sentiment_score'], g['cases_metric'])
    ).reset_index(name='correlation')
    temporal_corr = temporal_corr.dropna(subset=['correlation'])
    temporal_corr.to_csv(os.path.join(OUTPUT_DIR, f'temporal_correlation_{agg_level}.csv'), index=False)
    
    print("3. Computing Spatial Correlation (by county)...")
    spatial_corr = df.groupby('county_name').apply(
        lambda g: safe_pearson(g['sentiment_score'], g['cases_metric'])
    ).reset_index(name='correlation')
    spatial_corr = spatial_corr.dropna(subset=['correlation'])
    spatial_corr.to_csv(os.path.join(OUTPUT_DIR, f'spatial_correlation_{agg_level}.csv'), index=False)
    
    print("4. Computing Spatiotemporal Correlation (by UK COVID waves)...")
    # UK COVID wave definitions (adjusted to data range: Feb 2020 - Mar 2021)
    waves = {
        'Wave1': ('2020-02-01', '2020-06-30'),   # First wave: Feb-Jun 2020
        'Wave2': ('2020-07-01', '2020-11-30'),    # Second wave buildup: Jul-Nov 2020
        'Wave3': ('2020-12-01', '2021-03-31'),    # Third wave (Alpha): Dec 2020 - Mar 2021
    }
    
    for wave_name, (start_dt, end_dt) in waves.items():
        wave_df = df[(df['period'] >= start_dt) & (df['period'] <= end_dt)]
        if len(wave_df) > 0:
            wave_corr = wave_df.groupby('county_name').apply(
                lambda g: safe_pearson(g['sentiment_score'], g['cases_metric'])
            ).reset_index(name='correlation')
            wave_corr = wave_corr.dropna(subset=['correlation'])
            wave_corr.to_csv(os.path.join(OUTPUT_DIR, f'spatial_correlation_{agg_level}_{wave_name}.csv'), index=False)
            print(f"   => {wave_name}: {len(wave_corr)} counties with valid correlation")
        else:
            print(f"   => No data for {wave_name}")
            
    print("Correlation computation complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate correlations.")
    parser.add_argument('--agg-level', choices=['daily', 'weekly'], default='daily',
                        help="Aggregation level (daily or weekly)")
    args = parser.parse_args()
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    compute_correlations(args.agg_level)
