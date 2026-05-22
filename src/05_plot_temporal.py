import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')

def plot_temporal(agg_level):
    input_file = os.path.join(OUTPUT_DIR, f'temporal_correlation_{agg_level}.csv')
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Không tìm thấy file {input_file}. Vui lòng chạy 04_correlation.py trước.")
        return
        
    df['period'] = pd.to_datetime(df['period'])
    df = df.sort_values('period')
    
    plt.figure(figsize=(12, 6))
    
    # Plot line
    plt.plot(df['period'], df['correlation'], marker='o', linestyle='-', color='b', alpha=0.7)
    
    # Vẽ đường ngang y=0 để dễ nhìn
    plt.axhline(0, color='red', linestyle='--', alpha=0.5)
    
    plt.title(f'Temporal Correlation between Tweet Sentiment and COVID-19 Cases in the UK ({agg_level.capitalize()})')
    plt.xlabel('Time (Period)')
    plt.ylabel('Pearson Correlation (r)')
    plt.grid(True, alpha=0.3)
    
    # Định dạng trục X
    plt.gcf().autofmt_xdate()
    
    output_img = os.path.join(OUTPUT_DIR, f'temporal_correlation_{agg_level}.png')
    plt.tight_layout()
    plt.savefig(output_img, dpi=300)
    print(f"Đã lưu biểu đồ temporal correlation vào {output_img}")
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot temporal correlation.")
    parser.add_argument('--agg-level', choices=['daily', 'weekly'], default='daily',
                        help="Mức độ aggregate (daily hoặc weekly)")
    args = parser.parse_args()
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plot_temporal(args.agg_level)
