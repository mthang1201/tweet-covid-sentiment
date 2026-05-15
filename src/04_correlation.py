import os
import argparse
import pandas as pd
from scipy.stats import pearsonr

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')

def safe_pearson(x, y):
    """Tính pearson correlation an toàn, tránh lỗi nếu phương sai = 0 hoặc ít dữ liệu."""
    if len(x) < 3:
        return None
    # Nếu x hoặc y đều là hằng số (phương sai = 0)
    if x.nunique() == 1 or y.nunique() == 1:
        return None
    r, p = pearsonr(x, y)
    return r

def compute_correlations(agg_level):
    merged_file = os.path.join(OUTPUT_DIR, f'merged_data_{agg_level}.csv')
    try:
        df = pd.read_csv(merged_file)
    except FileNotFoundError:
        print(f"Không tìm thấy file {merged_file}. Vui lòng chạy 03_merge_data.py trước.")
        return
        
    df['period'] = pd.to_datetime(df['period'])
    
    print("1. Đang tính Global Correlation...")
    global_corr = safe_pearson(df['sentiment_score'], df['cases_metric'])
    print(f"   => Global Correlation: {global_corr}")
    with open(os.path.join(OUTPUT_DIR, f'global_correlation_{agg_level}.txt'), 'w') as f:
        f.write(f"Global Correlation: {global_corr}\n")
        
    print("2. Đang tính Temporal Correlation (theo thời gian)...")
    temporal_corr = df.groupby('period').apply(
        lambda g: safe_pearson(g['sentiment_score'], g['cases_metric'])
    ).reset_index(name='correlation')
    temporal_corr = temporal_corr.dropna(subset=['correlation'])
    temporal_corr.to_csv(os.path.join(OUTPUT_DIR, f'temporal_correlation_{agg_level}.csv'), index=False)
    
    print("3. Đang tính Spatial Correlation (theo không gian/county)...")
    spatial_corr = df.groupby('county_fips').apply(
        lambda g: safe_pearson(g['sentiment_score'], g['cases_metric'])
    ).reset_index(name='correlation')
    spatial_corr = spatial_corr.dropna(subset=['correlation'])
    spatial_corr.to_csv(os.path.join(OUTPUT_DIR, f'spatial_correlation_{agg_level}.csv'), index=False)
    
    print("4. Đang tính Spatiotemporal Correlation (theo các Wave)...")
    # Định nghĩa các Wave giống bài báo (nếu có dữ liệu khoảng này)
    waves = {
        'Wave1': ('2020-03-02', '2020-06-07'),
        'Wave2': ('2020-06-09', '2020-08-24'),
        'Wave3': ('2020-08-26', '2020-12-30')
    }
    
    for wave_name, (start_dt, end_dt) in waves.items():
        wave_df = df[(df['period'] >= start_dt) & (df['period'] <= end_dt)]
        if len(wave_df) > 0:
            wave_corr = wave_df.groupby('county_fips').apply(
                lambda g: safe_pearson(g['sentiment_score'], g['cases_metric'])
            ).reset_index(name='correlation')
            wave_corr = wave_corr.dropna(subset=['correlation'])
            wave_corr.to_csv(os.path.join(OUTPUT_DIR, f'spatial_correlation_{agg_level}_{wave_name}.csv'), index=False)
        else:
            print(f"   => Không có dữ liệu cho {wave_name}")
            
    print("Hoàn thành tính toán Correlation!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate correlations.")
    parser.add_argument('--agg-level', choices=['daily', 'weekly'], default='daily',
                        help="Mức độ aggregate (daily hoặc weekly)")
    args = parser.parse_args()
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    compute_correlations(args.agg_level)
