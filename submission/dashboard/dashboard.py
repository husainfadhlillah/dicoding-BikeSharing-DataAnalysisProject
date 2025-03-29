# Import
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import os 
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Set page configuration HARUS dipanggil pertama kali
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

# Custom CSS untuk gradient background
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
    .css-1d391kg {
        padding-top: 3rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load data
@st.cache_data
def load_data():
    hour_data = pd.read_csv('dashboard/hour_data_clean.csv')
    day_data = pd.read_csv('dashboard/day_data_clean.csv')
    return hour_data, day_data

hour_data, day_data = load_data()

# Konversi kolom tanggal
hour_data['dteday'] = pd.to_datetime(hour_data['dteday'])
day_data['dteday'] = pd.to_datetime(day_data['dteday'])

# Sidebar untuk filter data interaktif
st.sidebar.header("Filter Interaktif")
st.sidebar.markdown("**Filter Tanggal**")
date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    value=[hour_data['dteday'].min(), hour_data['dteday'].max()],
    min_value=hour_data['dteday'].min(),
    max_value=hour_data['dteday'].max()
)

st.sidebar.markdown("**Filter Lainnya**")
selected_year = st.sidebar.multiselect(
    "Pilih Tahun",
    options=hour_data['year'].unique(),
    default=hour_data['year'].unique()
)

selected_season = st.sidebar.multiselect(
    "Pilih Musim",
    options=hour_data['season_name'].unique(),
    default=hour_data['season_name'].unique()
)

selected_weather = st.sidebar.multiselect(
    "Pilih Kondisi Cuaca",
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

# Judul Dashboard
st.title("🚲 Bike Sharing Dashboard")
st.markdown("""
    Dashboard interaktif untuk menganalisis pola penggunaan sepeda berdasarkan waktu, cuaca, dan jenis pengguna.
""")

# Tab untuk organisasi konten
tab1, tab2, tab3 = st.tabs(["Pola Waktu", "Analisis Cuaca", "Segmentasi Pengguna"])

with tab1:
    st.header("📊 Analisis Pola Waktu")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Visualisasi Interaktif 1: Pola Penggunaan per Jam (Plotly)
        st.subheader("Pola Harian (Per Jam)")
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
        
        # Visualisasi 3: Heatmap Jam vs Hari (Plotly)
        st.subheader("Heatmap Jam vs Hari")
        hour_weekday_heatmap = hour_data.pivot_table(
            index='hr', 
            columns='weekday_name', 
            values='cnt', 
            aggfunc='mean'
        )
        hour_weekday_heatmap = hour_weekday_heatmap.reindex(
            columns=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        )
        
        fig3 = px.imshow(
            hour_weekday_heatmap,
            labels=dict(x="Hari", y="Jam", color="Penyewaan"),
            aspect="auto",
            color_continuous_scale='Viridis'
        )
        fig3.update_layout(
            title="Distribusi Penyewaan: Jam vs Hari",
            xaxis_title="Hari",
            yaxis_title="Jam"
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Visualisasi 2: Pola Bulanan (Plotly)
        st.subheader("Pola Bulanan")
        monthly_pattern = day_data.groupby(['month_name', 'mnth'])['cnt'].mean().reset_index().sort_values('mnth')
        
        fig2 = px.bar(
            monthly_pattern,
            x='month_name',
            y='cnt',
            labels={'month_name': 'Bulan', 'cnt': 'Rata-rata Penyewaan'},
            title='Rata-rata Penyewaan Sepeda per Bulan'
        )
        fig2.update_layout(
            xaxis_title="Bulan",
            yaxis_title="Rata-rata Penyewaan Harian",
            hovermode="x unified"
        )
        fig2.update_traces(
            hovertemplate="Bulan: %{x}<br>Penyewaan: %{y:.0f}<extra></extra>",
            marker_color='#636EFA'
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Visualisasi 4: RFM Analysis (Plotly)
        st.subheader("Analisis RFM Pengguna Registered")
        last_usage = hour_data.groupby('dteday')['registered'].sum().reset_index()
        last_usage['days_since_last'] = (hour_data['dteday'].max() - last_usage['dteday']).dt.days
        
        fig4 = px.histogram(
            last_usage,
            x='days_since_last',
            nbins=30,
            labels={'days_since_last': 'Hari Sejak Terakhir Penyewaan'},
            title='Distribusi Recency (Hari Sejak Terakhir Penyewaan)'
        )
        fig4.update_layout(
            xaxis_title="Hari",
            yaxis_title="Frekuensi"
        )
        st.plotly_chart(fig4, use_container_width=True)

with tab2:
    st.header("⛅ Analisis Pengaruh Cuaca")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Visualisasi 5: Pengaruh Cuaca (Plotly)
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
        fig5.update_traces(
            hovertemplate="Kondisi: %{x}<br>Penyewaan: %{y:.0f}<extra></extra>"
        )
        st.plotly_chart(fig5, use_container_width=True)
        
        # Visualisasi 7: Suhu vs Penyewaan (Plotly)
        st.subheader("Korelasi Suhu dan Penyewaan")
        fig7 = px.scatter(
            day_data,
            x='temp_actual',
            y='cnt',
            trendline="lowess",
            labels={'temp_actual': 'Suhu (°C)', 'cnt': 'Total Penyewaan'},
            title='Hubungan Suhu dan Total Penyewaan Harian',
            color='season_name',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig7.update_layout(
            xaxis_title="Suhu (°C)",
            yaxis_title="Total Penyewaan Harian"
        )
        st.plotly_chart(fig7, use_container_width=True)
    
    with col2:
        # Visualisasi 6: Cuaca per Musim (Plotly)
        st.subheader("Distribusi Cuaca per Musim")
        weather_season = hour_data.groupby(['season_name', 'weather_condition']).size().reset_index(name='count')
        weather_season['percentage'] = weather_season.groupby('season_name')['count'].apply(lambda x: x / x.sum() * 100)
        
        fig6 = px.bar(
            weather_season,
            x='season_name',
            y='percentage',
            color='weather_condition',
            labels={'season_name': 'Musim', 'percentage': 'Persentase (%)'},
            title='Distribusi Kondisi Cuaca per Musim',
            barmode='stack',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig6.update_layout(
            xaxis_title="Musim",
            yaxis_title="Persentase (%)",
            legend_title="Kondisi Cuaca"
        )
        fig6.update_traces(
            hovertemplate="Musim: %{x}<br>Kondisi: %{fullData.name}<br>Persentase: %{y:.1f}%<extra></extra>"
        )
        st.plotly_chart(fig6, use_container_width=True)
        
        # Visualisasi 8: Distribusi Cuaca per Grup Pengguna
        st.subheader("Cuaca per Intensitas Penggunaan")
        # Buat kategori pengguna berdasarkan quartile
        frequency = hour_data.groupby('dteday')['registered'].sum().reset_index()
        usage_groups = pd.qcut(frequency['registered'], q=4, labels=['Low', 'Medium', 'High', 'Very High'])
        frequency['usage_group'] = usage_groups
        merged_data = pd.merge(hour_data, frequency[['dteday', 'usage_group']], on='dteday')
        
        weather_by_group = merged_data.groupby(['usage_group', 'weather_condition']).size().unstack().fillna(0)
        weather_by_group_percentage = weather_by_group.div(weather_by_group.sum(axis=1), axis=0) * 100
        
        fig8 = px.bar(
            weather_by_group_percentage.reset_index(),
            x='usage_group',
            y=weather_by_group_percentage.columns,
            labels={'usage_group': 'Grup Pengguna', 'value': 'Persentase (%)'},
            title='Distribusi Kondisi Cuaca per Grup Pengguna',
            barmode='stack',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig8.update_layout(
            xaxis_title="Grup Pengguna",
            yaxis_title="Persentase (%)",
            legend_title="Kondisi Cuaca"
        )
        st.plotly_chart(fig8, use_container_width=True)

with tab3:
    st.header("👥 Segmentasi Pengguna")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Visualisasi 9: Proporsi Pengguna (Plotly)
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
        
        # Visualisasi 11: Pola Penggunaan Casual vs Registered per Jam
        st.subheader("Pola Penggunaan per Jam")
        user_type_hourly = hour_data.groupby('hr').agg({
            'casual': 'mean',
            'registered': 'mean'
        }).reset_index()
        
        fig11 = px.line(
            user_type_hourly,
            x='hr',
            y=['casual', 'registered'],
            labels={'hr': 'Jam', 'value': 'Rata-rata Penyewaan', 'variable': 'Tipe Pengguna'},
            title='Pola Penggunaan per Jam (Casual vs Registered)',
            color_discrete_sequence=['#FF9999', '#66B3FF']
        )
        fig11.update_layout(
            xaxis=dict(tickmode='linear', dtick=1),
            yaxis_title="Rata-rata Penyewaan",
            hovermode="x unified"
        )
        fig11.update_traces(
            line=dict(width=3),
            hovertemplate="Jam %{x}:00<br>Penyewaan: %{y:.1f}<extra></extra>"
        )
        st.plotly_chart(fig11, use_container_width=True)
    
    with col2:
        # Visualisasi 10: Penggunaan di Weekday vs Weekend
        st.subheader("Weekday vs Weekend")
        workday_agg = hour_data.groupby('workingday').agg({
            'casual': 'mean',
            'registered': 'mean'
        }).reset_index()
        workday_agg['workingday'] = workday_agg['workingday'].map({0: 'Weekend/Holiday', 1: 'Weekday'})
        
        fig10 = px.bar(
            workday_agg.melt(id_vars='workingday'),
            x='workingday',
            y='value',
            color='variable',
            labels={'workingday': 'Hari', 'value': 'Rata-rata Penyewaan', 'variable': 'Tipe Pengguna'},
            title='Rata-rata Penyewaan per Jam (Weekday vs Weekend)',
            barmode='group',
            color_discrete_sequence=['#FF9999', '#66B3FF']
        )
        fig10.update_layout(
            xaxis_title="",
            yaxis_title="Rata-rata Penyewaan per Jam"
        )
        fig10.update_traces(
            hovertemplate="%{x}<br>Tipe: %{fullData.name}<br>Penyewaan: %{y:.1f}<extra></extra>"
        )
        st.plotly_chart(fig10, use_container_width=True)
        
        # Visualisasi 12: Clustering Pola Penggunaan
        st.subheader("Clustering Pola Penggunaan")
        X = hour_data[['hr', 'cnt']]
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        kmeans = KMeans(n_clusters=3, random_state=42)
        hour_data['cluster'] = kmeans.fit_predict(X_scaled)
        
        fig12 = px.scatter(
            hour_data,
            x='hr',
            y='cnt',
            color='cluster',
            labels={'hr': 'Jam', 'cnt': 'Jumlah Penyewaan', 'cluster': 'Kluster'},
            title='Clustering Pola Penggunaan Sepeda',
            color_continuous_scale='Viridis'
        )
        fig12.update_layout(
            xaxis_title="Jam",
            yaxis_title="Jumlah Penyewaan",
            showlegend=True
        )
        fig12.update_traces(
            marker=dict(size=8, opacity=0.7),
            hovertemplate="Jam %{x}:00<br>Penyewaan: %{y}<br>Kluster: %{marker.color}<extra></extra>"
        )
        st.plotly_chart(fig12, use_container_width=True)

# Kesimpulan
st.header("📌 Kesimpulan & Rekomendasi")
with st.expander("Lihat Kesimpulan Lengkap"):
    st.markdown("""
    ### **Kesimpulan Analisis**
    1. **Pola Waktu**:
       - Penggunaan tertinggi pada jam 8 pagi (commuting) dan 17-18 sore (pulang kerja)
       - Weekend: distribusi merata dengan puncak siang hari (rekreasi)
       - Musim gugur (Fall) adalah periode dengan penggunaan tertinggi (+20% vs rata-rata)
    
    2. **Pengaruh Cuaca**:
       - Cuaca cerah menghasilkan 3.2x lebih banyak penyewaan dibanding cuaca buruk
       - Suhu optimal: 20-25°C (penurunan 2.7% per °C di bawah 10°C)
    
    3. **Segmentasi Pengguna**:
       - Registered users mendominasi (81.2%) dengan pola commuting yang jelas
       - Casual users (18.8%) lebih aktif di weekend (+38.4% vs weekday)
    
    ### **Rekomendasi Bisnis**
    1. **Manajemen Inventori**:
       - Tambah stok 40% pada jam sibuk (7-9 & 16-18) di hari kerja
       - Alokasi dinamis berdasarkan prediksi cuaca
    
    2. **Program Marketing**:
       - "Weekend Warrior Package" untuk konversi casual → registered
       - "Early Bird Reward" untuk retention pengguna registered
    
    3. **Pricing Strategy**:
       - Dynamic pricing (+15% pada peak hours, diskon 20% untuk cuaca buruk)
    """)

# Menampilkan data yang difilter
with st.expander("Lihat Data yang Difilter"):
    st.write(f"Menampilkan {len(hour_data)} baris data (per jam) dan {len(day_data)} baris data (harian)")
    st.dataframe(hour_data.head())