import os
import json
import argparse
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use
import matplotlib.pyplot as plt
import requests

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')

GEOJSON_URL = "https://raw.githubusercontent.com/evansd/uk-ceremonial-counties/master/uk-ceremonial-counties.geojson"
GEOJSON_PATH = os.path.join(DATA_DIR, 'uk_counties.geojson')

def ensure_geojson():
    """Download UK counties GeoJSON if not already present."""
    if os.path.exists(GEOJSON_PATH):
        print(f"GeoJSON already exists at {GEOJSON_PATH}")
        return True
    
    print(f"Downloading UK counties GeoJSON from {GEOJSON_URL}...")
    try:
        response = requests.get(GEOJSON_URL, timeout=30)
        response.raise_for_status()
        
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(GEOJSON_PATH, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("GeoJSON downloaded successfully!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading GeoJSON: {e}")
        return False

def plot_map(agg_level, wave=None):
    # Ensure we have the UK GeoJSON
    if not ensure_geojson():
        print("Cannot plot map without GeoJSON data.")
        return
    
    # Determine input/output file names
    if wave:
        input_file = os.path.join(OUTPUT_DIR, f'spatial_correlation_{agg_level}_{wave}.csv')
        output_img = os.path.join(OUTPUT_DIR, f'spatial_correlation_map_{agg_level}_{wave}.png')
        title = f'Spatial Correlation - United Kingdom\n({agg_level.capitalize()}, {wave})'
    else:
        input_file = os.path.join(OUTPUT_DIR, f'spatial_correlation_{agg_level}.csv')
        output_img = os.path.join(OUTPUT_DIR, f'spatial_correlation_map_{agg_level}.png')
        title = f'Spatial Correlation - United Kingdom\n({agg_level.capitalize()}, All Time)'
        
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"File {input_file} not found. Please run 04_correlation.py first.")
        return
        
    df['county_name'] = df['county_name'].astype(str)
    
    # Load UK GeoJSON
    try:
        gdf = gpd.read_file(GEOJSON_PATH)
    except Exception as e:
        print(f"Error reading GeoJSON {GEOJSON_PATH}: {e}")
        return
    
    # Extract county name from GeoJSON
    # UK ceremonial counties GeoJSON uses 'county' as the property name
    if 'county' in gdf.columns:
        gdf['county_name'] = gdf['county'].astype(str)
    elif 'NAME' in gdf.columns:
        gdf['county_name'] = gdf['NAME'].astype(str)
    else:
        # Try to find a suitable column
        print(f"GeoJSON columns: {gdf.columns.tolist()}")
        print("Could not find county name column in GeoJSON!")
        return
    
    # Print matching stats for debugging
    geo_counties = set(gdf['county_name'].unique())
    data_counties = set(df['county_name'].unique())
    matched = geo_counties.intersection(data_counties)
    print(f"GeoJSON counties: {len(geo_counties)}")
    print(f"Data counties: {len(data_counties)}")
    print(f"Matched counties: {len(matched)}")
    
    if len(matched) == 0:
        print("\nWARNING: No county names match between GeoJSON and data!")
        print(f"Sample GeoJSON counties: {sorted(list(geo_counties))[:10]}")
        print(f"Sample data counties: {sorted(list(data_counties))[:10]}")
        
    # Merge correlation data into geodataframe
    merged_gdf = gdf.merge(df, on='county_name', how='left')
    
    # Plot the map
    fig, ax = plt.subplots(1, 1, figsize=(12, 16))
    
    # Background for counties without data (grey)
    gdf.plot(ax=ax, color='#E0E0E0', edgecolor='white', linewidth=0.3)
    
    # Choropleth map for counties with correlation data
    # RdBu colormap: Red for negative correlation, Blue for positive
    counties_with_data = merged_gdf.dropna(subset=['correlation'])
    if len(counties_with_data) > 0:
        counties_with_data.plot(
            column='correlation', 
            ax=ax, 
            cmap='RdBu', 
            vmin=-1, 
            vmax=1,
            legend=True,
            legend_kwds={
                'label': "Pearson Correlation (r)", 
                'orientation': "horizontal", 
                'shrink': 0.6,
                'pad': 0.02
            },
            edgecolor='white',
            linewidth=0.3
        )
    
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_img, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved map to {output_img}")
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot spatial correlation map for the UK.")
    parser.add_argument('--agg-level', choices=['daily', 'weekly'], default='daily',
                        help="Aggregation level (daily or weekly)")
    parser.add_argument('--wave', type=str, default=None,
                        help="Wave name (e.g., Wave1, Wave2, Wave3)")
    args = parser.parse_args()
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plot_map(args.agg_level, args.wave)
