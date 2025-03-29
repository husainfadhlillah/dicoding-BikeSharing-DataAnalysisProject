# Import library
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import os 
import calendar

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
    hour_data = pd.read_csv('dashboard/hour_data_clean.csv')
    day_data = pd.read_csv('dashboard/day_data_clean.csv')
    
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

selected_user_type = st.sidebar.radio(
    "Jenis Pengguna",
    options=['Semua', 'Casual', 'Registered'],
    index=0
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

# Filter berdasarkan jenis pengguna
if selected_user_type == 'Casual':
    hour_data_filtered['cnt'] = hour_data_filtered['casual']
    day_data_filtered['cnt'] = day_data_filtered['casual']
elif selected_user_type == 'Registered':
    hour_data_filtered['cnt'] = hour_data_filtered['registered']
    day_data_filtered['cnt'] = day_data_filtered['registered']

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
        # Visualisasi 1: Pola penggunaan per jam (sesuai gambar notebook)
        st.subheader("Rata-rata Penyewaan Sepeda berdasarkan Jam")
        hourly_pattern = hour_data_filtered.groupby('hr')['cnt'].mean().reset_index()
        
        fig1, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(x='hr', y='cnt', data=hourly_pattern, marker='o', linewidth=2, ax=ax)
        ax.set_title('Rata-rata Penyewaan Sepeda berdasarkan Jam', fontsize=15)
        ax.set_xlabel('Jam', fontsize=12)
        ax.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
        ax.set_xticks(range(0, 24))
        ax.grid(True, alpha=0.3)
        st.pyplot(fig1)
        
    with col2:
        # Visualisasi 2: Heatmap jam vs hari (sesuai gambar notebook)
        st.subheader("Heatmap Penyewaan Sepeda: Jam vs Hari")
        hour_weekday_heatmap = hour_data_filtered.pivot_table(
            index='hr', 
            columns='weekday_name', 
            values='cnt', 
            aggfunc='mean'
        )
        hour_weekday_heatmap = hour_weekday_heatmap.reindex(
            columns=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        )
        
        fig2, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(hour_weekday_heatmap, cmap='viridis', annot=False, fmt='.0f', 
                   cbar_kws={'label': 'Rata-rata Penyewaan'}, ax=ax)
        ax.set_title('Heatmap Penyewaan Sepeda: Jam vs Hari', fontsize=16)
        ax.set_xlabel('Hari', fontsize=12)
        ax.set_ylabel('Jam', fontsize=12)
        st.pyplot(fig2)

with tab2:
    st.header("🌤️ Analisis Berdasarkan Cuaca")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Visualisasi 3: Pengaruh cuaca (sesuai gambar notebook)
        st.subheader("Rata-rata Penyewaan Sepeda berdasarkan Kondisi Cuaca")
        weather_impact = hour_data_filtered.groupby('weather_condition')['cnt'].mean().reset_index()
        
        fig3, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x='weather_condition', y='cnt', data=weather_impact, palette='viridis', ax=ax)
        ax.set_title('Rata-rata Penyewaan Sepeda berdasarkan Kondisi Cuaca', fontsize=15)
        ax.set_xlabel('Kondisi Cuaca', fontsize=12)
        ax.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
        ax.grid(True, alpha=0.3)
        st.pyplot(fig3)
        
    with col2:
        # Visualisasi 4: Distribusi cuaca per grup pengguna (sesuai notebook)
        st.subheader("Distribusi Kondisi Cuaca per Grup Pengguna")
        
        # Buat kategori pengguna berdasarkan quartile
        frequency = hour_data_filtered.groupby('dteday')['cnt'].sum().reset_index()
        usage_groups = pd.qcut(frequency['cnt'], q=4, labels=['Low', 'Medium', 'High', 'Very High'])
        frequency['usage_group'] = usage_groups
        merged_data = pd.merge(hour_data_filtered, frequency[['dteday', 'usage_group']], on='dteday')
        
        weather_by_group = merged_data.groupby(['usage_group', 'weather_condition']).size().unstack().fillna(0)
        weather_by_group_percentage = weather_by_group.div(weather_by_group.sum(axis=1), axis=0) * 100
        
        fig4, ax = plt.subplots(figsize=(12, 6))
        weather_by_group_percentage.plot(kind='bar', stacked=True, ax=ax)
        ax.set_title('Distribusi Kondisi Cuaca per Grup Pengguna')
        ax.set_xlabel('Grup Pengguna')
        ax.set_ylabel('Persentase (%)')
        ax.legend(title='Kondisi Cuaca', bbox_to_anchor=(1.05, 1))
        st.pyplot(fig4)

with tab3:
    st.header("👥 Analisis Berdasarkan Pengguna")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Visualisasi 5: Proporsi pengguna (sesuai gambar notebook)
        st.subheader("Proporsi Pengguna Casual vs Registered")
        
        if selected_user_type == 'Semua':
            total_users = day_data_filtered[['casual', 'registered']].sum()
            labels = ['Casual', 'Registered']
            
            fig5, ax = plt.subplots(figsize=(8, 6))
            ax.pie(total_users, labels=labels, autopct='%1.1f%%', startangle=90, 
                   colors=['#ff9999', '#66b3ff'])
            ax.set_title('Proporsi Pengguna Casual vs Registered', fontsize=15)
            ax.axis('equal')
            st.pyplot(fig5)
        else:
            st.info(f"Sedang menampilkan data untuk pengguna {selected_user_type} saja")
    
    with col2:
        # Visualisasi 6: Distribusi penyewaan per grup pengguna (sesuai notebook)
        st.subheader("Distribusi Penyewaan per Grup Pengguna")
        
        frequency = hour_data_filtered.groupby('dteday')['cnt'].sum().reset_index()
        usage_groups = pd.qcut(frequency['cnt'], q=4, labels=['Low', 'Medium', 'High', 'Very High'])
        frequency['usage_group'] = usage_groups
        
        fig6, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=frequency, x='usage_group', y='cnt', 
                   order=['Low', 'Medium', 'High', 'Very High'], ax=ax)
        ax.set_title('Distribusi Penyewaan per Grup Pengguna')
        ax.set_xlabel('Grup Pengguna')
        ax.set_ylabel('Jumlah Penyewaan per Hari')
        st.pyplot(fig6)

# Kesimpulan dan rekomendasi
st.header("📌 Kesimpulan dan Rekomendasi")
with st.expander("Lihat Detail"):
    st.markdown("""
    ### **Kesimpulan Analisis**
    1. **Pola Waktu**:
       - Puncak penggunaan pada jam 8 pagi (347.6 ± 58.2 penyewaan/jam) dan 17-18 sore (468.3 ± 72.1 penyewaan/jam)
       - Weekend menunjukkan pola berbeda dengan puncak siang hari
       - Musim gugur (Fall) memiliki penggunaan tertinggi (234 penyewaan/jam)
    
    2. **Pengaruh Cuaca**:
       - Cuaca cerah menghasilkan 205.4 penyewaan/jam (SD=112.3)
       - Heavy Rain mengurangi penyewaan hingga 63.4%
    
    3. **Segmentasi Pengguna**:
       - Registered users mendominasi (81.2%) dengan pola commuting yang jelas
       - Casual users (18.8%) lebih aktif di weekend
    
    ### **Rekomendasi Bisnis**
    1. **Manajemen Inventori**:
       - Tambah 40% stok sepeda pada jam sibuk (7-9 & 16-18) di hari kerja
       - Alokasi dinamis berdasarkan prediksi cuaca
    
    2. **Program Marketing**:
       - "Weekend Warrior Package" untuk konversi casual → registered
       - Program loyalitas "Early Bird Reward" untuk pengguna registered
    
    3. **Strategi Harga**:
       - Harga premium 15% pada jam sibuk weekday
       - Diskon 20% untuk jam 3-5 pagi dan cuaca buruk
    """)

# Tampilkan data yang difilter
with st.expander("Lihat Data Filtered"):
    st.write(f"Menampilkan {len(hour_data_filtered)} baris data (per jam)")
    st.dataframe(hour_data_filtered.head())