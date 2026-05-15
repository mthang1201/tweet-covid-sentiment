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
        
    df['county_fips'] = df['county_fips'].astype(str).str.zfill(5)
    
    # Load GeoJSON
    geojson_path = os.path.join(DATA_DIR, 'counties.geojson')
    try:
        gdf = gpd.read_file(geojson_path)
    except Exception as e:
        print(f"Lỗi đọc GeoJSON {geojson_path}: {e}")
        return
        
    # Trích xuất FIPS từ file GeoJSON (tùy định dạng, plotly geojson-counties-fips.json có id)
    if 'id' in gdf.columns:
        gdf['county_fips'] = gdf['id'].astype(str).str.zfill(5)
    elif 'FIPS' in gdf.columns:
        gdf['county_fips'] = gdf['FIPS'].astype(str).str.zfill(5)
    elif 'GEOID' in gdf.columns:
        gdf['county_fips'] = gdf['GEOID'].astype(str).str.zfill(5)
    else:
        print("Không tìm thấy cột chứa FIPS/ID trong GeoJSON!")
        return
        
    # Giới hạn bản đồ ở vùng nội địa Mỹ (Continental US) để tránh bản đồ bị méo
    # Giữ lại các FIPS không thuộc HI (15), AK (02), PR (72), VI (78), v.v.
    non_conus_states = ['02', '15', '60', '66', '69', '72', '74', '78']
    gdf = gdf[~gdf['county_fips'].str[:2].isin(non_conus_states)]
    
    # Merge dữ liệu correlation vào gdf
    merged_gdf = gdf.merge(df, on='county_fips', how='left')
    
    # Vẽ bản đồ
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
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
