# Import library
import streamlit as st
import pandas as pd
import plotly.express as px
import os 

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard Bike Sharing", layout="wide")

# CSS kustom untuk tampilan yang lebih baik
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    .css-1d391kg {
        padding-top: 3rem;
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
    return hour_data, day_data

hour_data, day_data = load_data()

# Konversi kolom tanggal
hour_data['dteday'] = pd.to_datetime(hour_data['dteday'])
day_data['dteday'] = pd.to_datetime(day_data['dteday'])

# Sidebar untuk filter interaktif
st.sidebar.header("Filter Data")
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
st.title("🚲 Dashboard Analisis Bike Sharing")
st.markdown("""
    Dashboard ini menampilkan analisis pola penggunaan sepeda berdasarkan waktu, cuaca, dan jenis pengguna.
""")

# Tab untuk organisasi konten
tab1, tab2, tab3 = st.tabs(["Analisis Waktu", "Analisis Cuaca", "Analisis Pengguna"])

with tab1:
    st.header("🕒 Analisis Berdasarkan Waktu")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Visualisasi 1: Pola Penggunaan per Jam
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
        
        # Visualisasi 3: Heatmap Jam vs Hari
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
        
        fig3 = px.imshow(
            hour_weekday_heatmap,
            labels=dict(x="Hari", y="Jam", color="Penyewaan"),
            aspect="auto",
            color_continuous_scale='Viridis',
            title='Heatmap: Penyewaan per Jam dan Hari'
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Visualisasi 2: Pola Bulanan
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
        
        # Visualisasi 4: Analisis Musiman
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
        st.plotly_chart(fig4, use_container_width=True)

with tab2:
    st.header("⛅ Analisis Berdasarkan Cuaca")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Visualisasi 5: Pengaruh Kondisi Cuaca
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
        fig5.update_layout(showlegend=False)
        st.plotly_chart(fig5, use_container_width=True)
        
        # Visualisasi 7: Suhu vs Penyewaan
        st.subheader("Pengaruh Suhu")
        fig7 = px.scatter(
            day_data,
            x='temp_actual',
            y='cnt',
            labels={'temp_actual': 'Suhu (°C)', 'cnt': 'Total Penyewaan'},
            title='Hubungan Suhu dan Total Penyewaan Harian',
            color='season_name',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig7, use_container_width=True)
    
    with col2:
        # Visualisasi 6: Cuaca per Musim
        st.subheader("Cuaca per Musim")
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
        fig6.update_layout(legend_title="Kondisi Cuaca")
        st.plotly_chart(fig6, use_container_width=True)
        
        # Visualisasi 8: Kelembaban vs Penyewaan
        st.subheader("Pengaruh Kelembaban")
        fig8 = px.scatter(
            day_data,
            x='hum_actual',
            y='cnt',
            labels={'hum_actual': 'Kelembaban (%)', 'cnt': 'Total Penyewaan'},
            title='Hubungan Kelembaban dan Total Penyewaan Harian',
            color='season_name',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig8, use_container_width=True)

with tab3:
    st.header("👥 Analisis Berdasarkan Jenis Pengguna")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Visualisasi 9: Proporsi Pengguna
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
        fig9.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig9, use_container_width=True)
        
        # Visualisasi 11: Pola Penggunaan per Jam
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
        fig11.update_layout(xaxis=dict(tickmode='linear', dtick=1))
        st.plotly_chart(fig11, use_container_width=True)
    
    with col2:
        # Visualisasi 10: Weekday vs Weekend
        st.subheader("Perbandingan Weekday vs Weekend")
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
        st.plotly_chart(fig10, use_container_width=True)
        
        # Visualisasi 12: Penggunaan per Musim
        st.subheader("Penggunaan per Musim")
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
        st.plotly_chart(fig12, use_container_width=True)

# Kesimpulan
st.header("📌 Kesimpulan & Rekomendasi")
with st.expander("Lihat Kesimpulan Lengkap"):
    st.markdown("""
    ### **Kesimpulan Analisis**
    1. **Pola Waktu**:
       - Penggunaan tertinggi pada jam 8 pagi (commuting) dan 17-18 sore (pulang kerja)
       - Weekend: distribusi merata dengan puncak siang hari (rekreasi)
       - Musim gugur (Fall) adalah periode dengan penggunaan tertinggi
    
    2. **Pengaruh Cuaca**:
       - Cuaca cerah menghasilkan penyewaan tertinggi
       - Cuaca buruk mengurangi penyewaan hingga 63%
    
    3. **Segmentasi Pengguna**:
       - Pengguna registered mendominasi (81.2%) dengan pola commuting
       - Pengguna casual (18.8%) lebih aktif di weekend
    
    ### **Rekomendasi Bisnis**
    1. **Manajemen Inventori**:
       - Tambah stok pada jam sibuk (7-9 & 16-18) di hari kerja
       - Kurangi stok dini hari (00.00-05.00)
    
    2. **Program Marketing**:
       - Targetkan pengguna casual di weekend untuk konversi ke registered
       - Berikan insentif untuk pengguna registered yang setia
    
    3. **Strategi Harga**:
       - Terapkan harga dinamis berdasarkan permintaan
       - Berikan diskon saat cuaca buruk untuk mempertahankan pengguna
    """)

# Menampilkan data yang difilter
with st.expander("Lihat Data yang Difilter"):
    st.write(f"Menampilkan {len(hour_data)} baris data (per jam) dan {len(day_data)} baris data (harian)")
    st.dataframe(hour_data.head())