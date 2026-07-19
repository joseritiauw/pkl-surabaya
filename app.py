import streamlit as st
import folium
from folium.plugins import Fullscreen, MiniMap, MousePosition
from streamlit_folium import st_folium
import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from shapely.geometry import Point
import os

st.set_page_config(page_title="Peta Interaktif Akses Bahan Baku PKL", layout="wide", initial_sidebar_state="expanded")

# CSS Injection for Enterprise WebGIS UI (Forcing Light Mode)
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Force Light Mode Theme globally */
    .stApp, .stApp > header { background-color: #FFFFFF !important; font-family: 'Inter', sans-serif !important; color: #2B2A28 !important; }
    .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp td, .stApp th {
        color: #2B2A28 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Reset layout padding */
    .block-container {
        padding-top: 86px !important; /* Header height */
        padding-bottom: 0px !important; 
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }
    
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Fixed Enterprise Header */
    .enterprise-header {
        background: #FFFFFF;
        height: 86px;
        box-sizing: border-box;
        position: fixed; top: 0; left: 0; right: 0; z-index: 999999;
        display: flex; justify-content: center; align-items: center;
        border-bottom: 1px solid #E5E7EB;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .header-title-box { display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; gap: 6px; }
    .header-title { font-family: 'Inter', sans-serif !important; font-size: 26px; font-weight: 700; margin: 0 !important; padding: 0 !important; color: #1E3A5F !important; letter-spacing: -0.5px; line-height: 1 !important; }
    .header-subtitle { font-family: 'Inter', sans-serif !important; font-size: 14px; color: #6B7280 !important; margin: 0 !important; padding: 0 !important; font-weight: 500; letter-spacing: 0.5px; line-height: 1 !important; }
    
    /* Force Map Iframe Fullscreen between header and footer */
    div.element-container:has(iframe),
    div[data-testid="stIFrame"],
    iframe { 
        position: fixed !important;
        top: 86px !important;
        bottom: 80px !important;
        left: 0 !important;
        right: 0 !important;
        width: 100vw !important;
        height: calc(100vh - 166px) !important;
        border-radius: 0 !important; 
        border: none !important; 
        margin: 0 !important; 
        z-index: 0 !important;
    }
    
    /* Fixed Bottom Executive Summary */
    .bottom-summary {
        background: #F8F9FA;
        border-top: 1px solid #DADCE0;
        position: fixed;
        bottom: 0; left: 0; right: 0;
        height: 80px;
        z-index: 999999;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0 40px;
    }
    .bottom-summary-text {
        color: #333333;
        font-size: 13px;
        line-height: 1.5;
        text-align: center;
        max-width: 1100px;
    }

    /* Sidebar Styling (Light Mode Forced) */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E5E7EB !important;
    }
    .sidebar-section-title {
        font-size: 12px;
        font-weight: 700;
        color: #1E3A5F;
        margin-top: 25px;
        margin-bottom: 12px;
        border-bottom: 1px solid #E5E7EB;
        padding-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .sidebar-stat-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 12px;
        font-size: 13px;
        color: #333333;
        align-items: center;
    }
    .sidebar-stat-val {
        font-weight: 700;
        color: #1E3A5F;
        font-size: 18px;
    }
    
    /* Clean up empty containers */
    .st-emotion-cache-1jicfl2 { padding: 0 !important; }
    div[data-testid="stVerticalBlock"] > div { margin-bottom: 0 !important; gap: 0 !important; }
    
    /* Hide st_folium auto-generated selection bounding boxes */
    path[fill="none"], path[fill-opacity="0"] { display: none !important; stroke-width: 0 !important; stroke: transparent !important; }
</style>
""", unsafe_allow_html=True)

# Render Enterprise Header
st.markdown("""
<div class="enterprise-header">
    <div class="header-title-box">
        <h2 class="header-title">Peta Interaktif Keadilan Spasial Akses Bahan Baku PKL Surabaya</h2>
        <p class="header-subtitle">Analisis spasial akses bahan baku PKL terhadap pasar tradisional di Kota Surabaya.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Functions ---

@st.cache_data
def load_data():
    """Load spatial data from GeoPackages."""
    data_dir = "Data"
    if not os.path.exists(data_dir):
        data_dir = "."
        
    def read_gpkg(filename):
        path = os.path.join(data_dir, filename)
        if os.path.exists(path):
            try:
                return gpd.read_file(path)
            except Exception:
                return None
        return None

    boundary = read_gpkg("boundary_surabaya_lvl3.gpkg")
    buffer = read_gpkg("buffered.gpkg")
    
    pasar = read_gpkg("pasar_tradisional.gpkg")
    if pasar is None:
        pasar = read_gpkg("pasar_tradisonal.gpkg")
        
    pkl_terlayani = read_gpkg("PKL_Terlayani.gpkg")
    blank_spot = read_gpkg("blank_spot.gpkg")
        
    return boundary, buffer, pasar, pkl_terlayani, blank_spot

def create_satellite_market(blank_spot_gdf):
    if blank_spot_gdf is None or len(blank_spot_gdf) == 0:
        return None
        
    coords = np.column_stack((blank_spot_gdf.geometry.x, blank_spot_gdf.geometry.y))
    n_clusters = min(3, len(coords))
    if n_clusters == 0:
        return None
        
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(coords)
    centroids = kmeans.cluster_centers_
    
    geometry = [Point(xy) for xy in centroids]
    data = {
        "Nama Pasar": [f"Pasar Satelit {i+1}" for i in range(n_clusters)],
        "Alasan": ["Berada di tengah konsentrasi PKL blank spot sehingga diharapkan mampu meningkatkan pemerataan akses bahan baku."] * n_clusters,
        "Cluster": [f"Cluster {i+1}" for i in range(n_clusters)]
    }
    
    return gpd.GeoDataFrame(data, geometry=geometry, crs=blank_spot_gdf.crs)

def get_popup_html(row, layer_type, columns):
    """Generate clean HTML table for popups matching dashboard style."""
    def find_val(keywords, default="-"):
        # 1. Cari exact match terlebih dahulu
        for col in columns:
            if col.lower() in [k.lower() for k in keywords]:
                val = row[col]
                if pd.notnull(val) and str(val).strip() != "" and str(val).lower() != "nan":
                    return val
        # 2. Jika tidak ada exact match, cari berdasarkan kata (substring)
        for col in columns:
            if col == 'geometry': continue
            for kw in keywords:
                if kw.lower() in col.lower():
                    val = row[col]
                    if pd.notnull(val) and str(val).strip() != "" and str(val).lower() != "nan":
                        return val
        return default

    html = "<div style='font-family: Inter, sans-serif; font-size: 12px; width: 230px;'>"
    html += "<table style='width: 100%; border-collapse: collapse;'>"
    
    if layer_type == "pasar":
        nama = find_val(["name", "nama", "pasar"])
        jam = find_val(["opening_hours", "jam", "operasional", "waktu", "open"])
        kapasitas = find_val(["capacity", "kapasitas", "capacity:persons"])
        html += f"<tr><th colspan='2' style='text-align: left; padding-bottom: 8px; font-size: 14px; border-bottom: 1px solid #1E3A5F; color: #1E3A5F;'>{nama}</th></tr>"
        html += f"<tr><td style='padding: 6px 0; color: #555; border-bottom: 1px solid #F3F4F6;'>Jam Operasional</td><td style='padding: 6px 0; text-align: right; font-weight: 600; color: #111; border-bottom: 1px solid #F3F4F6;'>{jam}</td></tr>"
        html += f"<tr><td style='padding: 6px 0; color: #555;'>Kapasitas</td><td style='padding: 6px 0; text-align: right; font-weight: 600; color: #111;'>{kapasitas}</td></tr>"
    elif layer_type == "pkl":
        nama = find_val(["name", "nama", "kawasan", "lokasi", "pkl"])
        jumlah = find_val(["jumlah", "count", "total"])
        status = find_val(["status", "keterangan"], default="-")
        html += f"<tr><th colspan='2' style='text-align: left; padding-bottom: 8px; font-size: 14px; border-bottom: 1px solid #1E3A5F; color: #1E3A5F;'>{nama}</th></tr>"
        html += f"<tr><td style='padding: 6px 0; color: #555; border-bottom: 1px solid #F3F4F6;'>Jumlah PKL</td><td style='padding: 6px 0; text-align: right; font-weight: 600; color: #111; border-bottom: 1px solid #F3F4F6;'>{jumlah}</td></tr>"
        html += f"<tr><td style='padding: 6px 0; color: #555;'>Status</td><td style='padding: 6px 0; text-align: right; font-weight: 600; color: #111;'>{status}</td></tr>"
    elif layer_type == "satelit":
        html += f"<tr><th colspan='2' style='text-align: left; padding-bottom: 8px; font-size: 14px; border-bottom: 1px solid #1E3A5F; color: #1E3A5F;'>{row['Nama Pasar']}</th></tr>"
        html += f"<tr><td colspan='2' style='padding: 6px 0; color: #555; line-height: 1.4; border-bottom: 1px solid #F3F4F6;'>{row['Alasan']}</td></tr>"
        html += f"<tr><td style='padding: 6px 0; color: #555;'>Cluster</td><td style='padding: 6px 0; text-align: right; font-weight: 600; color: #111;'>{row['Cluster']}</td></tr>"
    
    html += "</table></div>"
    return html

def create_map(boundary, buffer, pasar, pkl_terlayani, blank_spot, satelit, active_layers):
    """Create a professional full-viewport Folium map."""
    if boundary is not None and not boundary.empty:
        if boundary.crs and boundary.crs.to_epsg() != 4326:
            boundary = boundary.to_crs(epsg=4326)
        bounds = boundary.total_bounds
        center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]
    else:
        center = [-7.250445, 112.768845]

    m = folium.Map(location=center, zoom_start=12, tiles='CartoDB Positron', control_scale=True, zoom_control=True)

    Fullscreen().add_to(m)
    MiniMap(toggle_display=True, position='bottomleft').add_to(m)
    MousePosition(position='bottomright', separator=' | ', empty_string='NaN', lng_first=True, num_digits=5).add_to(m)

    if active_layers["Boundary"] and boundary is not None:
        if boundary.crs and boundary.crs.to_epsg() != 4326:
            boundary = boundary.to_crs(epsg=4326)
        folium.GeoJson(
            boundary,
            name="Boundary Surabaya",
            style_function=lambda feature: {
                'fillColor': '#ffffff', 
                'color': '#555555',     
                'weight': 1,
                'fillOpacity': 0.0
            },
            # Silent tooltip to prevent bounding box selection highlight artifacts
            tooltip=folium.GeoJsonTooltip(fields=[boundary.columns[0]], labels=False, style="display:none;")
        ).add_to(m)

    if active_layers["Buffer 3 KM"] and buffer is not None:
        if buffer.crs and buffer.crs.to_epsg() != 4326:
            buffer = buffer.to_crs(epsg=4326)
        folium.GeoJson(
            buffer,
            name="Buffer 3 KM",
            style_function=lambda feature: {
                'fillColor': '#3B82F6', 
                'color': '#3B82F6',
                'weight': 0.5,
                'fillOpacity': 0.15
            }
        ).add_to(m)

    if active_layers["Pasar Tradisional"] and pasar is not None:
        if pasar.crs and pasar.crs.to_epsg() != 4326:
            pasar = pasar.to_crs(epsg=4326)
        pasar_group = folium.FeatureGroup(name="Pasar Tradisional")
        for _, row in pasar.iterrows():
            if row.geometry and not row.geometry.is_empty:
                popup_html = get_popup_html(row, "pasar", pasar.columns)
                folium.CircleMarker(
                    location=[row.geometry.y, row.geometry.x],
                    radius=6,
                    color='#FFFFFF', # White outline for crispness
                    fill=True,
                    fill_color='#2E8B57',
                    fill_opacity=0.9,
                    weight=1,
                    popup=folium.Popup(popup_html, max_width=250)
                ).add_to(pasar_group)
        pasar_group.add_to(m)

    if active_layers["PKL Terlayani"] and pkl_terlayani is not None:
        if pkl_terlayani.crs and pkl_terlayani.crs.to_epsg() != 4326:
            pkl_terlayani = pkl_terlayani.to_crs(epsg=4326)
        if 'Status' not in pkl_terlayani.columns and 'status' not in pkl_terlayani.columns:
             pkl_terlayani['Status'] = 'Terlayani'
        pkl_t_group = folium.FeatureGroup(name="PKL Terlayani")
        for _, row in pkl_terlayani.iterrows():
            if row.geometry and not row.geometry.is_empty:
                popup_html = get_popup_html(row, "pkl", pkl_terlayani.columns)
                folium.CircleMarker(
                    location=[row.geometry.y, row.geometry.x],
                    radius=4,
                    color='#FFFFFF', 
                    fill=True,
                    fill_color='#71C671',
                    fill_opacity=0.9,
                    weight=1,
                    popup=folium.Popup(popup_html, max_width=250)
                ).add_to(pkl_t_group)
        pkl_t_group.add_to(m)

    if active_layers["Blank Spot"] and blank_spot is not None:
        if blank_spot.crs and blank_spot.crs.to_epsg() != 4326:
            blank_spot = blank_spot.to_crs(epsg=4326)
        if 'Status' not in blank_spot.columns and 'status' not in blank_spot.columns:
             blank_spot['Status'] = 'Blank Spot'
        blank_group = folium.FeatureGroup(name="Blank Spot")
        for _, row in blank_spot.iterrows():
            if row.geometry and not row.geometry.is_empty:
                popup_html = get_popup_html(row, "pkl", blank_spot.columns)
                folium.CircleMarker(
                    location=[row.geometry.y, row.geometry.x],
                    radius=5,
                    color='#FFFFFF',
                    fill=True,
                    fill_color='#D64545',
                    fill_opacity=0.9,
                    weight=1,
                    popup=folium.Popup(popup_html, max_width=250)
                ).add_to(blank_group)
        blank_group.add_to(m)

    if active_layers["Pasar Satelit"] and satelit is not None:
        if satelit.crs and satelit.crs.to_epsg() != 4326:
            satelit = satelit.to_crs(epsg=4326)
        satelit_group = folium.FeatureGroup(name="Pasar Satelit")
        for _, row in satelit.iterrows():
            if row.geometry and not row.geometry.is_empty:
                popup_html = get_popup_html(row, "satelit", satelit.columns)
                folium.Marker(
                    location=[row.geometry.y, row.geometry.x],
                    icon=folium.Icon(color='orange', icon='star', prefix='fa'),
                    popup=folium.Popup(popup_html, max_width=250)
                ).add_to(satelit_group)
        satelit_group.add_to(m)

    add_legend(m)
    folium.LayerControl(position='topright').add_to(m)
    return m

def add_legend(m):
    legend_html = '''
    <div style="position: fixed; bottom: 30px; right: 30px; width: 170px; 
                background: #FFFFFF; border: 1px solid #E5E7EB; z-index:9999; 
                font-size:12px; font-family: Inter, sans-serif;
                padding: 14px; border-radius: 6px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
        <div style="font-weight: 700; font-size: 11px; margin-bottom: 12px; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px;">Legenda</div>
        <div style="margin-bottom: 8px; display: flex; align-items: center; color: #333;"><i class="fa fa-circle" style="color:#2E8B57; font-size: 10px; width: 18px;"></i> Pasar Tradisional</div>
        <div style="margin-bottom: 8px; display: flex; align-items: center; color: #333;"><i class="fa fa-circle" style="color:#71C671; font-size: 10px; width: 18px;"></i> PKL Terlayani</div>
        <div style="margin-bottom: 8px; display: flex; align-items: center; color: #333;"><i class="fa fa-circle" style="color:#D64545; font-size: 10px; width: 18px;"></i> Blank Spot</div>
        <div style="margin-bottom: 8px; display: flex; align-items: center; color: #333;"><i class="fa fa-square" style="color:#3B82F6; opacity: 0.3; font-size: 12px; width: 18px;"></i> Buffer 3 KM</div>
        <div style="margin-bottom: 0px; display: flex; align-items: center; color: #333;"><i class="fa fa-star" style="color:#F4B400; font-size: 12px; width: 18px;"></i> Pasar Satelit</div>
    </div>
    <style>
    /* Reset margins for Folium Map internally */
    html, body { margin: 0 !important; padding: 0 !important; height: 100% !important; width: 100% !important; overflow: hidden !important; background-color: white !important; }
    .folium-map { height: 100% !important; width: 100% !important; position: absolute !important; top: 0 !important; left: 0 !important; bottom: 0 !important; right: 0 !important; }
    </style>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))


def main():
    # Load Data
    boundary, buffer, pasar, pkl_terlayani, blank_spot = load_data()
    satelit = create_satellite_market(blank_spot)
    
    # Sidebar
    with st.sidebar:
        st.markdown("<div class='sidebar-section-title'>Pengaturan Layer</div>", unsafe_allow_html=True)
        active_layers = {
            "Boundary": st.checkbox("Boundary", value=True),
            "Buffer 3 KM": st.checkbox("Buffer 3 KM", value=True),
            "Pasar Tradisional": st.checkbox("Pasar Tradisional", value=True),
            "PKL Terlayani": st.checkbox("PKL Terlayani", value=True),
            "Blank Spot": st.checkbox("Blank Spot", value=True),
            "Pasar Satelit": st.checkbox("Pasar Satelit", value=True)
        }
        
        st.markdown("<div class='sidebar-section-title'>Statistik Ringkas</div>", unsafe_allow_html=True)
        n_pasar = len(pasar) if pasar is not None else 89
        n_satelit = len(satelit) if satelit is not None else 3
        n_pkl_t = 126
        n_blank = 54
        
        st.markdown(f"""
        <div class='sidebar-stat-row'><span>Pasar Tradisional</span><span class='sidebar-stat-val'>{n_pasar}</span></div>
        <div class='sidebar-stat-row'><span>PKL Terlayani</span><span class='sidebar-stat-val'>{n_pkl_t}</span></div>
        <div class='sidebar-stat-row'><span>Blank Spot</span><span class='sidebar-stat-val'>{n_blank}</span></div>
        <div class='sidebar-stat-row'><span>Pasar Satelit</span><span class='sidebar-stat-val'>{n_satelit}</span></div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='sidebar-section-title'>Tentang Data</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 13px; color: #6B7280; line-height: 1.5;'>Data bersumber dari analisis spasial dengan radius pelayanan (buffer) 3 KM dari tiap pasar tradisional di Kota Surabaya. Clustering lokasi baru dilakukan menggunakan metode K-Means.</div>", unsafe_allow_html=True)
    
    # Render Map
    m = create_map(boundary, buffer, pasar, pkl_terlayani, blank_spot, satelit, active_layers)
    # The returned height here is irrelevant because CSS calc() forces it to fill viewport
    st_folium(m, use_container_width=True, height=1200, returned_objects=[])

    # Render Bottom Summary Fixed
    st.markdown("""
    <div class="bottom-summary">
        <div class="bottom-summary-text">
            <b>Ringkasan Analisis:</b> Berdasarkan hasil analisis spasial, terdapat 180 titik PKL di Kota Surabaya dengan 126 titik (70%) berada dalam jangkauan pelayanan pasar tradisional. Sisanya, sebanyak 54 titik (30%) berada pada area blank spot yang tidak terlayani. Melalui algoritma K-Means Clustering, sistem merekomendasikan 3 lokasi Pasar Satelit baru. Pembangunan pada lokasi ini diharapkan dapat meningkatkan pemerataan akses bahan baku secara signifikan bagi PKL yang sebelumnya tidak terjangkau.
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
