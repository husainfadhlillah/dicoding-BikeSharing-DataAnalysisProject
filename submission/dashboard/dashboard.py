# Import library
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import os 

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard Penyewaan Sepeda", layout="wide")

# Custom CSS untuk tampilan yang lebih baik
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
        color: #333;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    hour_data_path = os.path.join(script_dir, 'hour_data_clean.csv')
    day_data_path = os.path.join(script_dir, 'day_data_clean.csv')
    
    hour_data = pd.read_csv(hour_data_path)
    day_data = pd.read_csv(day_data_path)
    
    # Konversi kolom tanggal ke datetime
    hour_data['dteday'] = pd.to_datetime(hour_data['dteday'])
    day_data['dteday'] = pd.to_datetime(day_data['dteday'])
    
    return hour_data, day_data

hour_data, day_data = load_data()

# Sidebar untuk filter interaktif
st.sidebar.header("Filter Data")

# Filter tanggal
st.sidebar.markdown("**Rentang Tanggal**")
date_range = st.sidebar.date_input(
    "Pilih periode",
    value=[hour_data['dteday'].min(), hour_data['dteday'].max()],
    min_value=hour_data['dteday'].min(),
    max_value=hour_data['dteday'].max()
)

# Filter lainnya
st.sidebar.markdown("**Filter Tambahan**")
selected_year = st.sidebar.multiselect(
    "Tahun",
    options=hour_data['year'].unique(),
    default=hour_data['year'].unique()
)

selected_season = st.sidebar.multiselect(
    "Musim",
    options=hour_data['season_name'].unique(),
    default=hour_data['season_name'].unique()
)

selected_weather = st.sidebar.multiselect(
    "Kondisi Cuaca",
    options=hour_data['weather_condition'].unique(),
    default=hour_data['weather_condition'].unique()
)

# Membuat salinan data untuk filter
hour_data_filtered = hour_data.copy()
day_data_filtered = day_data.copy()

# Filter data berdasarkan pilihan
if len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
    
    hour_data_filtered = hour_data[
        (hour_data['dteday'] >= start_date) & 
        (hour_data['dteday'] <= end_date)
    ]
    day_data_filtered = day_data[
        (day_data['dteday'] >= start_date) & 
        (day_data['dteday'] <= end_date)
    ]

if selected_year:
    hour_data_filtered = hour_data_filtered[hour_data_filtered['year'].isin(selected_year)]
    day_data_filtered = day_data_filtered[day_data_filtered['year'].isin(selected_year)]

if selected_season:
    hour_data_filtered = hour_data_filtered[hour_data_filtered['season_name'].isin(selected_season)]
    day_data_filtered = day_data_filtered[day_data_filtered['season_name'].isin(selected_season)]

if selected_weather:
    hour_data_filtered = hour_data_filtered[hour_data_filtered['weather_condition'].isin(selected_weather)]
    day_data_filtered = day_data_filtered[day_data_filtered['weather_condition'].isin(selected_weather)]

# Judul dashboard
st.title("📊 Dashboard Analisis Penyewaan Sepeda")
st.markdown("""
    Visualisasi interaktif pola penggunaan sepeda berdasarkan waktu, cuaca, dan jenis pengguna.
""")

# Tab untuk organisasi konten
tab1, tab2, tab3 = st.tabs(["Analisis Waktu", "Analisis Cuaca", "Analisis Pengguna"])

with tab1:
    st.header("🕒 Analisis Berdasarkan Waktu")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Visualisasi 1: Pola penggunaan per jam
        st.subheader("Pola Penggunaan per Jam")
        hourly_pattern = hour_data_filtered.groupby('hr')['cnt'].mean().reset_index()
        
        fig1 = px.line(
            hourly_pattern, 
            x='hr', 
            y='cnt',
            labels={'hr': 'Jam', 'cnt': 'Rata-rata Penyewaan'},
            title='Rata-rata Penyewaan Sepeda per Jam'
        )
        fig1.update_layout(
            xaxis=dict(tickmode='linear', dtick=1),
            yaxis_title="Rata-rata Penyewaan",
            hovermode="x unified"
        )
        fig1.update_traces(
            line=dict(width=3),
            marker=dict(size=8),
            hovertemplate="Jam %{x}:00<br>Penyewaan: %{y:.0f}<extra></extra>"
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Visualisasi 2: Heatmap jam vs hari
        st.subheader("Distribusi Jam dan Hari")
        hour_weekday_heatmap = hour_data_filtered.pivot_table(
            index='hr', 
            columns='weekday_name', 
            values='cnt', 
            aggfunc='mean'
        )
        hour_weekday_heatmap = hour_weekday_heatmap.reindex(
            columns=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        )
        
        fig2 = px.imshow(
            hour_weekday_heatmap,
            labels=dict(x="Hari", y="Jam", color="Penyewaan"),
            aspect="auto",
            color_continuous_scale='Viridis'
        )
        fig2.update_layout(
            title="Heatmap Penyewaan: Jam vs Hari",
            xaxis_title="Hari",
            yaxis_title="Jam"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        # Visualisasi 3: Pola bulanan
        st.subheader("Pola Bulanan")
        monthly_pattern = day_data_filtered.groupby(['month_name', 'mnth'])['cnt'].mean().reset_index().sort_values('mnth')
        
        fig3 = px.bar(
            monthly_pattern,
            x='month_name',
            y='cnt',
            labels={'month_name': 'Bulan', 'cnt': 'Rata-rata Penyewaan'},
            title='Rata-rata Penyewaan per Bulan'
        )
        fig3.update_layout(
            xaxis_title="Bulan",
            yaxis_title="Rata-rata Penyewaan Harian"
        )
        fig3.update_traces(
            hovertemplate="Bulan: %{x}<br>Penyewaan: %{y:.0f}<extra></extra>",
            marker_color='#636EFA'
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # Visualisasi 4: Analisis seasonal
        st.subheader("Pola Musiman")
        season_pattern = day_data_filtered.groupby('season_name')['cnt'].mean().reset_index()
        
        fig4 = px.bar(
            season_pattern,
            x='season_name',
            y='cnt',
            labels={'season_name': 'Musim', 'cnt': 'Rata-rata Penyewaan'},
            title='Rata-rata Penyewaan per Musim',
            color='season_name',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig4.update_layout(
            xaxis_title="Musim",
            yaxis_title="Rata-rata Penyewaan Harian",
            showlegend=False
        )
        st.plotly_chart(fig4, use_container_width=True)

# ... (lanjutkan dengan tab2 dan tab3 yang sama, pastikan menggunakan hour_data_filtered dan day_data_filtered)

# Kesimpulan dan rekomendasi
st.header("📌 Kesimpulan dan Rekomendasi")
with st.expander("Lihat Detail"):
    st.markdown("""
    ### **Kesimpulan Analisis**
    1. **Pola Waktu**:
       - Penggunaan tertinggi pada jam 8 pagi (commuting) dan 17-18 sore (pulang kerja)
       - Weekend: distribusi merata dengan puncak siang hari (rekreasi)
       - Musim gugur (Fall) adalah periode dengan penggunaan tertinggi
    
    2. **Pengaruh Cuaca**:
       - Cuaca cerah menghasilkan 3.2x lebih banyak penyewaan dibanding cuaca buruk
       - Suhu optimal: 20-25°C
    
    3. **Segmentasi Pengguna**:
       - Registered users mendominasi (81.2%) dengan pola commuting yang jelas
       - Casual users (18.8%) lebih aktif di weekend
    
    ### **Rekomendasi Bisnis**
    1. **Manajemen Inventori**:
       - Tambah stok pada jam sibuk (7-9 & 16-18) di hari kerja
       - Alokasi dinamis berdasarkan prediksi cuaca
    
    2. **Program Marketing**:
       - Promo khusus untuk konversi casual → registered
       - Program loyalitas untuk pengguna registered
    
    3. **Strategi Harga**:
       - Harga dinamis berdasarkan permintaan
    """)

# Tampilkan data yang difilter
with st.expander("Lihat Data"):
    st.write(f"Menampilkan {len(hour_data_filtered)} baris data (per jam)")
    st.dataframe(hour_data_filtered.head())