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

# Filter data berdasarkan pilihan
if len(date_range) == 2:
    hour_data = hour_data[
        (hour_data['dteday'] >= pd.to_datetime(date_range[0])) &
        (hour_data['dteday'] <= pd.to_datetime(date_range[1]))
    ]
    day_data = day_data[
        (day_data['dteday'] >= pd.to_datetime(date_range[0])) &
        (day_data['dteday'] <= pd.to_datetime(date_range[1]))
    ]

if selected_year:
    hour_data = hour_data[hour_data['year'].isin(selected_year)]
    day_data = day_data[day_data['year'].isin(selected_year)]

if selected_season:
    hour_data = hour_data[hour_data['season_name'].isin(selected_season)]
    day_data = day_data[day_data['season_name'].isin(selected_season)]

if selected_weather:
    hour_data = hour_data[hour_data['weather_condition'].isin(selected_weather)]
    day_data = day_data[day_data['weather_condition'].isin(selected_weather)]

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
        hourly_pattern = hour_data.groupby('hr')['cnt'].mean().reset_index()
        
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
        hour_weekday_heatmap = hour_data.pivot_table(
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
        monthly_pattern = day_data.groupby(['month_name', 'mnth'])['cnt'].mean().reset_index().sort_values('mnth')
        
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
        season_pattern = day_data.groupby('season_name')['cnt'].mean().reset_index()
        
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

with tab2:
    st.header("⛅ Analisis Berdasarkan Cuaca")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Visualisasi 5: Pengaruh kondisi cuaca
        st.subheader("Pengaruh Kondisi Cuaca")
        weather_impact = hour_data.groupby('weather_condition')['cnt'].mean().reset_index()
        
        fig5 = px.bar(
            weather_impact,
            x='weather_condition',
            y='cnt',
            labels={'weather_condition': 'Kondisi Cuaca', 'cnt': 'Rata-rata Penyewaan'},
            title='Rata-rata Penyewaan berdasarkan Kondisi Cuaca',
            color='weather_condition',
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        fig5.update_layout(
            xaxis_title="Kondisi Cuaca",
            yaxis_title="Rata-rata Penyewaan per Jam",
            showlegend=False
        )
        st.plotly_chart(fig5, use_container_width=True)
        
        # Visualisasi 6: Suhu vs penyewaan
        st.subheader("Pengaruh Suhu")
        fig6 = px.scatter(
            day_data,
            x='temp_actual',
            y='cnt',
            trendline="lowess",
            labels={'temp_actual': 'Suhu (°C)', 'cnt': 'Total Penyewaan'},
            title='Hubungan Suhu dan Total Penyewaan',
            color='season_name',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig6.update_layout(
            xaxis_title="Suhu (°C)",
            yaxis_title="Total Penyewaan Harian"
        )
        st.plotly_chart(fig6, use_container_width=True)
    
    with col2:
        # Visualisasi 7: Cuaca per musim
        st.subheader("Distribusi Cuaca per Musim")
        weather_season = hour_data.groupby(['season_name', 'weather_condition']).size().reset_index(name='count')
        weather_season['percentage'] = weather_season.groupby('season_name')['count'].apply(lambda x: x / x.sum() * 100)
        
        fig7 = px.bar(
            weather_season,
            x='season_name',
            y='percentage',
            color='weather_condition',
            labels={'season_name': 'Musim', 'percentage': 'Persentase (%)'},
            title='Distribusi Kondisi Cuaca per Musim',
            barmode='stack',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig7.update_layout(
            xaxis_title="Musim",
            yaxis_title="Persentase (%)",
            legend_title="Kondisi Cuaca"
        )
        st.plotly_chart(fig7, use_container_width=True)
        
        # Visualisasi 8: Kelembaban vs penyewaan
        st.subheader("Pengaruh Kelembaban")
        fig8 = px.scatter(
            day_data,
            x='hum_actual',
            y='cnt',
            labels={'hum_actual': 'Kelembaban (%)', 'cnt': 'Total Penyewaan'},
            title='Hubungan Kelembaban dan Total Penyewaan',
            color='weather_condition'
        )
        fig8.update_layout(
            xaxis_title="Kelembaban (%)",
            yaxis_title="Total Penyewaan Harian"
        )
        st.plotly_chart(fig8, use_container_width=True)

with tab3:
    st.header("👥 Analisis Berdasarkan Jenis Pengguna")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Visualisasi 9: Proporsi pengguna
        st.subheader("Proporsi Pengguna")
        total_users = day_data[['casual', 'registered']].sum().reset_index()
        total_users.columns = ['user_type', 'count']
        
        fig9 = px.pie(
            total_users,
            values='count',
            names='user_type',
            labels={'user_type': 'Tipe Pengguna', 'count': 'Jumlah'},
            title='Proporsi Pengguna Casual vs Registered',
            color_discrete_sequence=['#FF9999', '#66B3FF'],
            hole=0.3
        )
        fig9.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate="%{label}: %{value} (%{percent})<extra></extra>"
        )
        st.plotly_chart(fig9, use_container_width=True)
        
        # Visualisasi 10: Pola penggunaan per jam
        st.subheader("Pola Penggunaan per Jam")
        user_type_hourly = hour_data.groupby('hr').agg({
            'casual': 'mean',
            'registered': 'mean'
        }).reset_index()
        
        fig10 = px.line(
            user_type_hourly,
            x='hr',
            y=['casual', 'registered'],
            labels={'hr': 'Jam', 'value': 'Rata-rata Penyewaan', 'variable': 'Tipe Pengguna'},
            title='Pola Penggunaan per Jam (Casual vs Registered)',
            color_discrete_sequence=['#FF9999', '#66B3FF']
        )
        fig10.update_layout(
            xaxis=dict(tickmode='linear', dtick=1),
            yaxis_title="Rata-rata Penyewaan",
            hovermode="x unified"
        )
        st.plotly_chart(fig10, use_container_width=True)
    
    with col2:
        # Visualisasi 11: Weekday vs weekend
        st.subheader("Perbandingan Weekday vs Weekend")
        workday_agg = hour_data.groupby('workingday').agg({
            'casual': 'mean',
            'registered': 'mean'
        }).reset_index()
        workday_agg['workingday'] = workday_agg['workingday'].map({0: 'Weekend/Holiday', 1: 'Weekday'})
        
        fig11 = px.bar(
            workday_agg.melt(id_vars='workingday'),
            x='workingday',
            y='value',
            color='variable',
            labels={'workingday': 'Hari', 'value': 'Rata-rata Penyewaan', 'variable': 'Tipe Pengguna'},
            title='Rata-rata Penyewaan per Jam (Weekday vs Weekend)',
            barmode='group',
            color_discrete_sequence=['#FF9999', '#66B3FF']
        )
        fig11.update_layout(
            xaxis_title="",
            yaxis_title="Rata-rata Penyewaan per Jam"
        )
        st.plotly_chart(fig11, use_container_width=True)
        
        # Visualisasi 12: Penggunaan per musim
        st.subheader("Pola Penggunaan per Musim")
        user_type_season = hour_data.groupby('season_name').agg({
            'casual': 'mean',
            'registered': 'mean'
        }).reset_index()
        
        fig12 = px.bar(
            user_type_season.melt(id_vars='season_name'),
            x='season_name',
            y='value',
            color='variable',
            labels={'season_name': 'Musim', 'value': 'Rata-rata Penyewaan', 'variable': 'Tipe Pengguna'},
            title='Rata-rata Penyewaan per Musim (Casual vs Registered)',
            barmode='group',
            color_discrete_sequence=['#FF9999', '#66B3FF']
        )
        fig12.update_layout(
            xaxis_title="Musim",
            yaxis_title="Rata-rata Penyewaan per Jam"
        )
        st.plotly_chart(fig12, use_container_width=True)

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
    st.write(f"Menampilkan {len(hour_data)} baris data (per jam)")
    st.dataframe(hour_data.head())