import os
import argparse
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')

def plot_map(agg_level, wave=None):
    # Lắp ráp tên file
    if wave:
        input_file = os.path.join(OUTPUT_DIR, f'spatial_correlation_{agg_level}_{wave}.csv')
        output_img = os.path.join(OUTPUT_DIR, f'spatial_correlation_map_{agg_level}_{wave}.png')
        title = f'Spatial Correlation ({agg_level.capitalize()}, {wave})'
    else:
        input_file = os.path.join(OUTPUT_DIR, f'spatial_correlation_{agg_level}.csv')
        output_img = os.path.join(OUTPUT_DIR, f'spatial_correlation_map_{agg_level}.png')
        title = f'Spatial Correlation ({agg_level.capitalize()}, All time)'
        
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Không tìm thấy file {input_file}. Vui lòng chạy 04_correlation.py trước.")
        return
        
    # Chuyển đổi ID để map với county_name
    df['county_name'] = df['county_name'].astype(str)
    
    # Load GeoJSON
    geojson_path = os.path.join(DATA_DIR, 'uk_counties.geojson')
    try:
        gdf = gpd.read_file(geojson_path)
    except Exception as e:
        print(f"Lỗi đọc GeoJSON {geojson_path}: {e}")
        return
        
    # Trích xuất county name từ file GeoJSON (UK ceremonial counties dùng 'county')
    if 'county' in gdf.columns:
        gdf['county_name'] = gdf['county'].astype(str)
    elif 'LAD13NM' in gdf.columns:
        gdf['county_name'] = gdf['LAD13NM'].astype(str)
    else:
        print("Không tìm thấy cột chứa tên county trong GeoJSON!")
        return
        
    # Merge dữ liệu correlation vào gdf
    merged_gdf = gdf.merge(df, on='county_name', how='left')
    
    # Vẽ bản đồ
    fig, ax = plt.subplots(1, 1, figsize=(15, 15)) # Tăng kích thước height cho UK map
    
    # Nền cho các county không có dữ liệu (màu xám)
    gdf.plot(ax=ax, color='lightgrey', edgecolor='white', linewidth=0.1)
    
    # Choropleth map cho các county có dữ liệu
    # Dùng colormap RdBu (Red-Blue), giới hạn vmin=-1, vmax=1 vì đây là Pearson correlation
    merged_gdf.dropna(subset=['correlation']).plot(
        column='correlation', 
        ax=ax, 
        cmap='RdBu', 
        vmin=-1, 
        vmax=1,
        legend=True,
        legend_kwds={'label': "Pearson Correlation", 'orientation': "horizontal", 'shrink': 0.6},
        edgecolor='white',
        linewidth=0.1
    )
    
    ax.set_title(title, fontsize=16)
    ax.axis('off') # Ẩn trục tọa độ
    
    plt.tight_layout()
    plt.savefig(output_img, dpi=300, bbox_inches='tight')
    print(f"Đã lưu bản đồ vào {output_img}")
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot spatial correlation map.")
    parser.add_argument('--agg-level', choices=['daily', 'weekly'], default='daily',
                        help="Mức độ aggregate (daily hoặc weekly)")
    parser.add_argument('--wave', type=str, default=None,
                        help="Tên Wave (nếu có, VD: Wave1, Wave2...)")
    args = parser.parse_args()
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plot_map(args.agg_level, args.wave)
