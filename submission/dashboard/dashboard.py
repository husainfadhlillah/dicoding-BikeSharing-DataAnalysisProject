# Import library
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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
    h1, h2, h3 {
        color: #2c3e50; /* Warna judul yang lebih gelap dan modern */
    }
    .stTabs [data-baseweb="tab-list"] {
		gap: 24px; /* Jarak antar tab */
	}
	.stTabs [data-baseweb="tab"] {
		height: 50px;
        white-space: pre-wrap;
		background-color: #e0e0e0; /* Warna tab tidak aktif */
		border-radius: 4px 4px 0px 0px;
		gap: 1px;
		padding-top: 10px;
		padding-bottom: 10px;
        color: #4a4a4a; /* Warna teks tab tidak aktif */
	}
	.stTabs [aria-selected="true"] {
  		background-color: #007bff; /* Warna tab aktif (biru cerah) */
        color: white; /* Warna teks tab aktif */
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

hour_df, day_df = load_data()

# --- Sidebar untuk Filter Interaktif ---
st.sidebar.header("⚙️ Filter Data Interaktif")

# Filter Rentang Tanggal
st.sidebar.markdown("**Pilih Rentang Tanggal**")
if not day_df.empty and 'dteday' in day_df.columns:
    min_date_val = day_df['dteday'].min()
    max_date_val = day_df['dteday'].max()
    
    # Menggunakan try-except untuk mengatasi potensi masalah dengan nilai default date_input
    try:
        date_range = st.sidebar.date_input(
            "Periode Analisis:",
            value=(min_date_val, max_date_val), # Default ke rentang penuh
            min_value=min_date_val,
            max_value=max_date_val,
            key="date_filter"
        )
        # Pastikan date_range selalu memiliki dua elemen (awal dan akhir)
        if len(date_range) == 1: # Jika hanya satu tanggal dipilih (mungkin saat interaksi awal)
            date_range = (date_range[0], max_date_val)
    except Exception as e:
        st.sidebar.error(f"Error pada filter tanggal: {e}. Menggunakan rentang default.")
        date_range = (min_date_val, max_date_val)
else:
    st.sidebar.warning("Data harian tidak tersedia atau kolom 'dteday' tidak ditemukan. Filter tanggal dinonaktifkan.")
    # Sediakan nilai default jika data tidak ada untuk menghindari error lebih lanjut
    date_range = (pd.Timestamp('2011-01-01'), pd.Timestamp('2012-12-31'))


# Filter Tambahan dari Kolom Kategorikal
st.sidebar.markdown("**Filter Kategorikal Lainnya**")

# Filter Tahun (jika ada dan relevan)
if 'year' in hour_df.columns:
    unique_years = sorted(hour_df['year'].unique())
    selected_year = st.sidebar.multiselect(
        "Tahun:",
        options=unique_years,
        default=unique_years, # Default semua tahun terpilih
        key="year_filter"
    )
else:
    selected_year = []

# Filter Musim
if 'season_name' in hour_df.columns:
    season_order_options = ['Spring', 'Summer', 'Fall', 'Winter']
    # Filter opsi berdasarkan yang ada di data, sambil mempertahankan urutan
    available_seasons_in_order = [s for s in season_order_options if s in hour_df['season_name'].unique()]
    selected_season = st.sidebar.multiselect(
        "Musim:",
        options=available_seasons_in_order,
        default=available_seasons_in_order, # Default semua musim terpilih
        key="season_filter"
    )
else:
    selected_season = []

# Filter Kondisi Cuaca
if 'weather_condition' in hour_df.columns:
    weather_order_options = ['Clear/Few clouds', 'Mist/Cloudy', 'Light Snow/Rain', 'Heavy Rain/Snow/Fog']
    available_weather_in_order = [w for w in weather_order_options if w in hour_df['weather_condition'].unique()]
    selected_weather = st.sidebar.multiselect(
        "Kondisi Cuaca:",
        options=available_weather_in_order,
        default=available_weather_in_order, # Default semua kondisi cuaca terpilih
        key="weather_filter"
    )
else:
    selected_weather = []

# Filter Jenis Pengguna
selected_user_type = st.sidebar.radio(
    "Jenis Pengguna:",
    options=['Semua', 'Casual', 'Registered'],
    index=0, # Default 'Semua'
    key="user_type_filter"
)

# --- Proses Filter Data ---
hour_data_filtered = hour_df.copy()
day_data_filtered = day_df.copy()

# Terapkan filter tanggal
if len(date_range) == 2: # Pastikan ada tanggal awal dan akhir
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
    if not hour_data_filtered.empty:
        hour_data_filtered = hour_data_filtered[
            (hour_data_filtered['dteday'] >= start_date) & (hour_data_filtered['dteday'] <= end_date)
        ]
    if not day_data_filtered.empty:
        day_data_filtered = day_data_filtered[
            (day_data_filtered['dteday'] >= start_date) & (day_data_filtered['dteday'] <= end_date)
        ]

# Terapkan filter tahun
if selected_year and 'year' in hour_data_filtered.columns:
    hour_data_filtered = hour_data_filtered[hour_data_filtered['year'].isin(selected_year)]
if selected_year and 'year' in day_data_filtered.columns:
    day_data_filtered = day_data_filtered[day_data_filtered['year'].isin(selected_year)]

# Terapkan filter musim
if selected_season and 'season_name' in hour_data_filtered.columns:
    hour_data_filtered = hour_data_filtered[hour_data_filtered['season_name'].isin(selected_season)]
if selected_season and 'season_name' in day_data_filtered.columns:
    day_data_filtered = day_data_filtered[day_data_filtered['season_name'].isin(selected_season)]

# Terapkan filter kondisi cuaca
if selected_weather and 'weather_condition' in hour_data_filtered.columns:
    hour_data_filtered = hour_data_filtered[hour_data_filtered['weather_condition'].isin(selected_weather)]
if selected_weather and 'weather_condition' in day_data_filtered.columns:
    day_data_filtered = day_data_filtered[day_data_filtered['weather_condition'].isin(selected_weather)]


# Filter berdasarkan jenis pengguna untuk kolom 'cnt_display'
# Inisialisasi kolom 'cnt_display' untuk menghindari error jika dataframe kosong
if not hour_data_filtered.empty:
    if 'cnt' not in hour_data_filtered.columns: # Jika 'cnt' tidak ada, buat kolom dummy
        hour_data_filtered['cnt'] = 0
    if 'casual' not in hour_data_filtered.columns:
        hour_data_filtered['casual'] = 0
    if 'registered' not in hour_data_filtered.columns:
        hour_data_filtered['registered'] = 0
    
    if selected_user_type == 'Casual':
        hour_data_filtered['cnt_display'] = hour_data_filtered['casual']
    elif selected_user_type == 'Registered':
        hour_data_filtered['cnt_display'] = hour_data_filtered['registered']
    else: # Semua
        hour_data_filtered['cnt_display'] = hour_data_filtered['cnt']
else: # Jika hour_data_filtered kosong, buat DataFrame kosong dengan kolom yang diperlukan
    hour_data_filtered = pd.DataFrame(columns=hour_df.columns.tolist() + ['cnt_display'])


if not day_data_filtered.empty:
    if 'cnt' not in day_data_filtered.columns:
        day_data_filtered['cnt'] = 0
    if 'casual' not in day_data_filtered.columns:
        day_data_filtered['casual'] = 0
    if 'registered' not in day_data_filtered.columns:
        day_data_filtered['registered'] = 0

    if selected_user_type == 'Casual':
        day_data_filtered['cnt_display'] = day_data_filtered['casual']
    elif selected_user_type == 'Registered':
        day_data_filtered['cnt_display'] = day_data_filtered['registered']
    else: # Semua
        day_data_filtered['cnt_display'] = day_data_filtered['cnt']
else:
    day_data_filtered = pd.DataFrame(columns=day_df.columns.tolist() + ['cnt_display'])


# --- Judul Dashboard ---
st.title("🚴‍♂️ Dashboard Analisis Penyewaan Sepeda")
st.markdown("""
    Selamat datang di dashboard interaktif analisis penyewaan sepeda. 
    Gunakan filter di sidebar untuk menjelajahi data berdasarkan periode waktu, musim, cuaca, dan jenis pengguna.
""")

# --- Tab untuk Organisasi Konten ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Pola Waktu & Musiman", 
    "☀️ Pengaruh Cuaca", 
    "👥 Analisis Pengguna", 
    "🔬 Analisis Lanjutan (Segmen Waktu)"
])

# Order konstanta untuk plot
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
month_order = calendar.month_name[1:]
season_order = ['Spring', 'Summer', 'Fall', 'Winter']
weather_order = ['Clear/Few clouds', 'Mist/Cloudy', 'Light Snow/Rain', 'Heavy Rain/Snow/Fog']
time_of_day_order = ['Pagi (05-10)', 'Siang (11-15)', 'Sore (16-20)', 'Malam (21-04)']


with tab1:
    st.header("🕒 Pola Penggunaan Sepeda Berdasarkan Waktu")
    
    if not hour_data_filtered.empty and 'cnt_display' in hour_data_filtered.columns:
        col1a, col1b = st.columns(2)
        
        with col1a:
            st.subheader("Rata-rata Penyewaan per Jam")
            hourly_pattern = hour_data_filtered.groupby('hr')['cnt_display'].mean().reset_index()
            if not hourly_pattern.empty:
                fig_hr, ax_hr = plt.subplots(figsize=(10, 5))
                sns.lineplot(x='hr', y='cnt_display', data=hourly_pattern, marker='o', linewidth=2, ax=ax_hr, color='dodgerblue')
                ax_hr.set_title('Rata-rata Penyewaan per Jam', fontsize=15)
                ax_hr.set_xlabel('Jam dalam Sehari', fontsize=12)
                ax_hr.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
                ax_hr.set_xticks(range(0, 24))
                ax_hr.grid(True, linestyle='--', alpha=0.7)
                st.pyplot(fig_hr)
            else:
                st.info("Tidak ada data penyewaan per jam untuk filter yang dipilih.")

            st.subheader("Rata-rata Penyewaan per Musim")
            seasonal_pattern_tab1 = hour_data_filtered.groupby('season_name')['cnt_display'].mean()
            if not seasonal_pattern_tab1.empty:
                seasonal_pattern_tab1 = seasonal_pattern_tab1.reindex(season_order).reset_index()
                fig_season_t1, ax_season_t1 = plt.subplots(figsize=(10, 5))
                sns.barplot(x='season_name', y='cnt_display', data=seasonal_pattern_tab1, palette='viridis', ax=ax_season_t1)
                ax_season_t1.set_title('Rata-rata Penyewaan per Musim', fontsize=15)
                ax_season_t1.set_xlabel('Musim', fontsize=12)
                ax_season_t1.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
                ax_season_t1.grid(True, axis='y', linestyle='--', alpha=0.7)
                st.pyplot(fig_season_t1)
            else:
                st.info("Tidak ada data penyewaan per musim untuk filter yang dipilih.")

        with col1b:
            st.subheader("Rata-rata Penyewaan per Hari")
            daily_pattern_weekday = hour_data_filtered.groupby('weekday_name')['cnt_display'].mean()
            if not daily_pattern_weekday.empty:
                daily_pattern_weekday = daily_pattern_weekday.reindex(weekday_order).reset_index()
                fig_day, ax_day = plt.subplots(figsize=(10, 5))
                sns.barplot(x='weekday_name', y='cnt_display', data=daily_pattern_weekday, palette='crest', ax=ax_day)
                ax_day.set_title('Rata-rata Penyewaan per Hari dalam Seminggu', fontsize=15)
                ax_day.set_xlabel('Hari', fontsize=12)
                ax_day.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
                ax_day.tick_params(axis='x', rotation=30)
                ax_day.grid(True, axis='y', linestyle='--', alpha=0.7)
                st.pyplot(fig_day)
            else:
                st.info("Tidak ada data penyewaan per hari untuk filter yang dipilih.")

            st.subheader("Rata-rata Penyewaan per Bulan")
            monthly_pattern = hour_data_filtered.groupby('month_name')['cnt_display'].mean()
            if not monthly_pattern.empty:
                monthly_pattern = monthly_pattern.reindex(month_order).reset_index()
                fig_month, ax_month = plt.subplots(figsize=(10, 5))
                sns.lineplot(x='month_name', y='cnt_display', data=monthly_pattern, marker='o', linewidth=2, color='mediumseagreen', sort=False, ax=ax_month)
                ax_month.set_title('Rata-rata Penyewaan per Bulan', fontsize=15)
                ax_month.set_xlabel('Bulan', fontsize=12)
                ax_month.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
                ax_month.tick_params(axis='x', rotation=45)
                ax_month.grid(True, linestyle='--', alpha=0.7)
                st.pyplot(fig_month)
            else:
                st.info("Tidak ada data penyewaan per bulan untuk filter yang dipilih.")
        
        st.markdown("---")
        st.subheader("Heatmap Pola Penyewaan")
        col_hm1, col_hm2 = st.columns(2)
        with col_hm1:
            st.markdown("##### Jam vs Hari dalam Seminggu")
            hour_weekday_heatmap_df = hour_data_filtered.pivot_table(index='hr', columns='weekday_name', values='cnt_display', aggfunc='mean')
            if not hour_weekday_heatmap_df.empty:
                hour_weekday_heatmap_df = hour_weekday_heatmap_df.reindex(columns=weekday_order)
                fig_hm_day, ax_hm_day = plt.subplots(figsize=(10, 7))
                sns.heatmap(hour_weekday_heatmap_df, cmap='viridis', annot=False, fmt=".0f", linewidths=.5, 
                            cbar_kws={'label': 'Rata-rata Penyewaan'}, ax=ax_hm_day)
                ax_hm_day.set_title('Heatmap: Jam vs Hari', fontsize=14)
                ax_hm_day.set_xlabel('Hari', fontsize=11)
                ax_hm_day.set_ylabel('Jam', fontsize=11)
                st.pyplot(fig_hm_day)
            else:
                st.info("Tidak ada data heatmap jam vs hari untuk filter yang dipilih.")

        with col_hm2:
            st.markdown("##### Jam vs Bulan")
            hour_month_heatmap_df = hour_data_filtered.pivot_table(index='hr', columns='month_name', values='cnt_display', aggfunc='mean')
            if not hour_month_heatmap_df.empty:
                hour_month_heatmap_df = hour_month_heatmap_df.reindex(columns=month_order)
                fig_hm_month, ax_hm_month = plt.subplots(figsize=(10, 7))
                sns.heatmap(hour_month_heatmap_df, cmap='YlGnBu', annot=False, fmt=".0f", linewidths=.5, 
                            cbar_kws={'label': 'Rata-rata Penyewaan'}, ax=ax_hm_month)
                ax_hm_month.set_title('Heatmap: Jam vs Bulan', fontsize=14)
                ax_hm_month.set_xlabel('Bulan', fontsize=11)
                ax_hm_month.set_ylabel('Jam', fontsize=11)
                ax_hm_month.tick_params(axis='x', rotation=45, ha='right')
                st.pyplot(fig_hm_month)
            else:
                st.info("Tidak ada data heatmap jam vs bulan untuk filter yang dipilih.")
    else:
        st.warning("Tidak ada data untuk ditampilkan di tab Pola Waktu berdasarkan filter yang Anda pilih.")

with tab2:
    st.header("☀️ Pengaruh Kondisi Cuaca terhadap Penyewaan")
    
    if not hour_data_filtered.empty and 'cnt_display' in hour_data_filtered.columns:
        col2a, col2b = st.columns([6, 4]) # Kolom pertama lebih lebar
        
        with col2a:
            st.subheader("Rata-rata Penyewaan berdasarkan Kondisi Cuaca")
            weather_impact_df = hour_data_filtered.groupby('weather_condition')['cnt_display'].mean()
            if not weather_impact_df.empty:
                weather_impact_df = weather_impact_df.reindex(weather_order).reset_index()
                fig_weather, ax_weather = plt.subplots(figsize=(10, 6))
                sns.barplot(x='weather_condition', y='cnt_display', data=weather_impact_df, palette='coolwarm', ax=ax_weather)
                ax_weather.set_title('Pengaruh Kondisi Cuaca terhadap Rata-rata Penyewaan', fontsize=15)
                ax_weather.set_xlabel('Kondisi Cuaca', fontsize=12)
                ax_weather.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
                ax_weather.tick_params(axis='x', rotation=15, ha='right')
                ax_weather.grid(True, axis='y', linestyle='--', alpha=0.7)
                st.pyplot(fig_weather)

                # Tambahan dari Notebook: Rata-rata suhu dan kelembapan per kondisi cuaca
                weather_params_df = hour_data_filtered.groupby('weather_condition').agg(
                    avg_temp_actual=('temp_actual', 'mean'),
                    avg_hum_actual=('hum_actual', 'mean')
                ).reindex(weather_order).reset_index()

                if not weather_params_df.empty:
                    st.markdown("##### Parameter Cuaca Rata-rata per Kondisi:")
                    st.dataframe(weather_params_df.set_index('weather_condition').style.format("{:.2f}"))

            else:
                st.info("Tidak ada data dampak cuaca untuk filter yang dipilih.")
            
        with col2b:
            st.subheader("Distribusi Penyewaan")
            if 'temp_actual' in hour_data_filtered.columns and 'hum_actual' in hour_data_filtered.columns:
                fig_scatter_temp, ax_scatter_temp = plt.subplots(figsize=(8,5))
                sns.scatterplot(x='temp_actual', y='cnt_display', data=hour_data_filtered, alpha=0.5, ax=ax_scatter_temp, color='red')
                ax_scatter_temp.set_title('Penyewaan vs Suhu Aktual (°C)', fontsize=14)
                ax_scatter_temp.set_xlabel('Suhu Aktual (°C)', fontsize=11)
                ax_scatter_temp.set_ylabel('Jumlah Penyewaan', fontsize=11)
                st.pyplot(fig_scatter_temp)

                fig_scatter_hum, ax_scatter_hum = plt.subplots(figsize=(8,5))
                sns.scatterplot(x='hum_actual', y='cnt_display', data=hour_data_filtered, alpha=0.5, ax=ax_scatter_hum, color='blue')
                ax_scatter_hum.set_title('Penyewaan vs Kelembapan Aktual (%)', fontsize=14)
                ax_scatter_hum.set_xlabel('Kelembapan Aktual (%)', fontsize=11)
                ax_scatter_hum.set_ylabel('Jumlah Penyewaan', fontsize=11)
                st.pyplot(fig_scatter_hum)
            else:
                st.info("Kolom suhu atau kelembapan tidak tersedia untuk scatter plot.")


        st.markdown("---")
        st.subheader("Heatmap Penyewaan: Jam vs Kondisi Cuaca")
        hour_weather_heatmap_df = hour_data_filtered.pivot_table(index='hr', columns='weather_condition', values='cnt_display', aggfunc='mean')
        if not hour_weather_heatmap_df.empty:
            hour_weather_heatmap_df = hour_weather_heatmap_df.reindex(columns=weather_order, fill_value=0)
            fig_hm_weather, ax_hm_weather = plt.subplots(figsize=(10, 8))
            sns.heatmap(hour_weather_heatmap_df, cmap='coolwarm_r', annot=True, fmt=".0f", linewidths=.5, 
                        cbar_kws={'label': 'Rata-rata Penyewaan'}, ax=ax_hm_weather)
            ax_hm_weather.set_title('Heatmap: Jam vs Kondisi Cuaca', fontsize=16)
            ax_hm_weather.set_xlabel('Kondisi Cuaca', fontsize=12)
            ax_hm_weather.set_ylabel('Jam', fontsize=12)
            ax_hm_weather.tick_params(axis='x', rotation=15, ha='right')
            st.pyplot(fig_hm_weather)
        else:
            st.info("Tidak ada data heatmap jam vs kondisi cuaca untuk filter yang dipilih.")
    else:
        st.warning("Tidak ada data untuk ditampilkan di tab Pengaruh Cuaca berdasarkan filter yang Anda pilih.")


with tab3:
    st.header("👥 Analisis Berdasarkan Jenis Pengguna")
    
    # Hanya tampilkan bagian ini jika filter 'Semua' atau data harian ada
    if not day_data_filtered.empty and 'casual' in day_data_filtered.columns and 'registered' in day_data_filtered.columns:
        st.subheader("Proporsi Pengguna Casual vs Registered (Keseluruhan Periode Terfilter)")
        total_users_pie_data = day_data_filtered[['casual', 'registered']].sum()
        if total_users_pie_data.sum() > 0:
            labels_pie = ['Casual', 'Registered']
            fig_pie_users, ax_pie_users = plt.subplots(figsize=(8, 5))
            ax_pie_users.pie(total_users_pie_data, labels=labels_pie, autopct='%1.1f%%', startangle=140, 
                            colors=['#ff9999','#66b3ff'], wedgeprops={'edgecolor': 'grey'})
            ax_pie_users.set_title('Proporsi Total Penyewaan: Casual vs Registered', fontsize=15)
            ax_pie_users.axis('equal') 
            st.pyplot(fig_pie_users)
        else:
            st.info("Tidak ada data penyewaan untuk ditampilkan dalam diagram proporsi.")
    else:
        st.info("Data harian tidak cukup untuk menampilkan proporsi pengguna. Periksa filter Anda.")

    st.markdown("---")
    
    # Grafik perbandingan hanya jika 'Semua' pengguna dipilih di filter atau jika data per jam ada
    if not hour_data_filtered.empty and ('casual' in hour_data_filtered.columns and 'registered' in hour_data_filtered.columns):
        # Filter untuk pengguna 'Semua' akan menampilkan perbandingan, selain itu akan menampilkan data untuk tipe yang dipilih
        if selected_user_type == "Semua":
            st.subheader("Perbandingan Pola Penggunaan: Casual vs Registered")
            col3a, col3b = st.columns(2)

            with col3a:
                st.markdown("##### Berdasarkan Jam")
                user_type_hourly_df = hour_data_filtered.groupby('hr').agg(
                    avg_casual=('casual', 'mean'),
                    avg_registered=('registered', 'mean')
                ).reset_index()
                if not user_type_hourly_df.empty:
                    fig_user_hr, ax_user_hr = plt.subplots(figsize=(10,5))
                    ax_user_hr.plot(user_type_hourly_df['hr'], user_type_hourly_df['avg_casual'], label='Casual', marker='o', color='skyblue', linewidth=2)
                    ax_user_hr.plot(user_type_hourly_df['hr'], user_type_hourly_df['avg_registered'], label='Registered', marker='x', color='darkblue', linewidth=2)
                    ax_user_hr.set_title('Rata-rata Penyewaan per Jam', fontsize=14)
                    ax_user_hr.set_xlabel('Jam', fontsize=11)
                    ax_user_hr.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=11)
                    ax_user_hr.set_xticks(range(0,24,2))
                    ax_user_hr.legend()
                    ax_user_hr.grid(True, linestyle='--', alpha=0.7)
                    st.pyplot(fig_user_hr)
                else:
                    st.info("Tidak ada data perbandingan pengguna per jam.")

                st.markdown("##### Berdasarkan Hari Kerja vs Akhir Pekan/Libur")
                # workingday: 0=Akhir Pekan/Libur, 1=Hari Kerja
                workday_agg_df = hour_data_filtered.groupby('workingday').agg(
                    avg_casual=('casual', 'mean'),
                    avg_registered=('registered', 'mean')
                ).reset_index()
                if not workday_agg_df.empty:
                    workday_agg_df['workingday_label'] = workday_agg_df['workingday'].map({0: 'Akhir Pekan/Libur', 1: 'Hari Kerja'})
                    workday_melted = workday_agg_df.melt(id_vars='workingday_label', value_vars=['avg_casual', 'avg_registered'], 
                                                        var_name='tipe_pengguna', value_name='rata_penyewaan')
                    workday_melted['tipe_pengguna'] = workday_melted['tipe_pengguna'].map({'avg_casual': 'Casual', 'avg_registered': 'Registered'})
                    
                    fig_workday, ax_workday = plt.subplots(figsize=(8, 5))
                    sns.barplot(x='workingday_label', y='rata_penyewaan', hue='tipe_pengguna', data=workday_melted, 
                                palette={'Casual': 'skyblue', 'Registered': 'darkblue'}, ax=ax_workday)
                    ax_workday.set_title('Penyewaan di Hari Kerja vs Akhir Pekan', fontsize=14)
                    ax_workday.set_xlabel('Status Hari', fontsize=11)
                    ax_workday.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=11)
                    ax_workday.legend(title="Tipe Pengguna")
                    st.pyplot(fig_workday)
                else:
                    st.info("Tidak ada data perbandingan pengguna berdasarkan status hari.")

            with col3b:
                st.markdown("##### Berdasarkan Musim")
                user_type_season_df = hour_data_filtered.groupby('season_name').agg(
                    avg_casual=('casual', 'mean'),
                    avg_registered=('registered', 'mean')
                )
                if not user_type_season_df.empty:
                    user_type_season_df = user_type_season_df.reindex(season_order).reset_index()
                    user_type_season_melted = user_type_season_df.melt(id_vars='season_name', value_vars=['avg_casual', 'avg_registered'], 
                                                                    var_name='tipe_pengguna', value_name='rata_penyewaan')
                    user_type_season_melted['tipe_pengguna'] = user_type_season_melted['tipe_pengguna'].map({'avg_casual': 'Casual', 'avg_registered': 'Registered'})

                    fig_user_season, ax_user_season = plt.subplots(figsize=(10,5))
                    sns.barplot(x='season_name', y='rata_penyewaan', hue='tipe_pengguna', data=user_type_season_melted, 
                                palette={'Casual': 'skyblue', 'Registered': 'darkblue'}, ax=ax_user_season)
                    ax_user_season.set_title('Rata-rata Penyewaan per Musim', fontsize=14)
                    ax_user_season.set_xlabel('Musim', fontsize=11)
                    ax_user_season.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=11)
                    ax_user_season.legend(title="Tipe Pengguna")
                    st.pyplot(fig_user_season)
                else:
                    st.info("Tidak ada data perbandingan pengguna per musim.")
        
        elif selected_user_type != "Semua" and not hour_data_filtered.empty and 'cnt_display' in hour_data_filtered.columns:
            # Jika filter pengguna spesifik (Casual atau Registered) dipilih, tampilkan pola untuk tipe tersebut
            st.subheader(f"Pola Penggunaan untuk Pengguna {selected_user_type}")
            # Anda dapat menambahkan visualisasi spesifik untuk tipe pengguna yang dipilih di sini
            # Contoh: Pola per jam untuk pengguna yang difilter
            user_specific_hourly = hour_data_filtered.groupby('hr')['cnt_display'].mean().reset_index()
            if not user_specific_hourly.empty:
                fig_user_spec_hr, ax_user_spec_hr = plt.subplots(figsize=(10,5))
                sns.lineplot(x='hr', y='cnt_display', data=user_specific_hourly, marker='o', ax=ax_user_spec_hr, label=selected_user_type)
                ax_user_spec_hr.set_title(f'Rata-rata Penyewaan per Jam ({selected_user_type})', fontsize=14)
                ax_user_spec_hr.set_xlabel('Jam', fontsize=11)
                ax_user_spec_hr.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=11)
                ax_user_spec_hr.legend()
                ax_user_spec_hr.grid(True, linestyle='--', alpha=0.7)
                st.pyplot(fig_user_spec_hr)
            else:
                st.info(f"Tidak ada data pola per jam untuk pengguna {selected_user_type} dengan filter saat ini.")
    else:
        st.warning("Tidak ada data untuk ditampilkan di tab Analisis Pengguna berdasarkan filter yang Anda pilih, atau kolom 'casual'/'registered' tidak tersedia.")


with tab4:
    st.header("🔬 Analisis Lanjutan: Segmentasi Pengguna Berdasarkan Waktu Penggunaan Harian")
    st.markdown("""
    Analisis ini mengelompokkan jam dalam sehari menjadi empat segmen waktu untuk memahami karakteristik penggunaan sepeda lebih detail pada setiap segmen.
    """)
    
    if not hour_data_filtered.empty and all(c in hour_data_filtered.columns for c in ['hr', 'cnt_display', 'casual', 'registered', 'temp_actual', 'weather_condition']):
        # Fungsi untuk Manual Grouping berdasarkan waktu
        def assign_time_of_day(hr_val):
            if 5 <= hr_val <= 10: return 'Pagi (05-10)'
            elif 11 <= hr_val <= 15: return 'Siang (11-15)'
            elif 16 <= hr_val <= 20: return 'Sore (16-20)'
            else: return 'Malam (21-04)'

        # Buat salinan untuk analisis ini agar tidak mempengaruhi df filter utama
        adv_analysis_df = hour_data_filtered.copy()
        adv_analysis_df['time_of_day'] = adv_analysis_df['hr'].apply(assign_time_of_day)
        
        time_of_day_analysis_df = adv_analysis_df.groupby('time_of_day').agg(
            avg_total_users=('cnt_display', 'mean'),
            avg_casual_users=('casual', 'mean'),
            avg_registered_users=('registered', 'mean'),
            avg_temp_actual=('temp_actual', 'mean')
        ).reindex(time_of_day_order) # Pastikan urutan benar

        if not time_of_day_analysis_df.empty:
            fig_adv, axes = plt.subplots(2, 2, figsize=(16, 12)) # Perbesar ukuran plot
            fig_adv.suptitle('Karakteristik Penyewaan Sepeda per Segmen Waktu Harian', fontsize=18, y=1.02)

            # 1. Rata-rata Total Penyewaan per Segmen Waktu
            sns.barplot(x=time_of_day_analysis_df.index, y='avg_total_users', data=time_of_day_analysis_df, ax=axes[0,0], palette='Blues_r', order=time_of_day_order)
            axes[0,0].set_title('Rata-rata Total Penyewaan', fontsize=14)
            axes[0,0].set_xlabel('Segmen Waktu', fontsize=12)
            axes[0,0].set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
            axes[0,0].tick_params(axis='x', rotation=20, ha='right')
            axes[0,0].grid(True, axis='y', linestyle='--', alpha=0.7)

            # 2. Rata-rata Pengguna Casual vs Registered per Segmen Waktu
            time_of_day_melted_adv = time_of_day_analysis_df[['avg_casual_users', 'avg_registered_users']].reset_index().melt(id_vars='time_of_day', var_name='user_type', value_name='avg_users')
            time_of_day_melted_adv['user_type'] = time_of_day_melted_adv['user_type'].map({'avg_casual_users':'Casual', 'avg_registered_users':'Registered'})
            
            sns.barplot(x='time_of_day', y='avg_users', hue='user_type', data=time_of_day_melted_adv, ax=axes[0,1], 
                        palette={'Casual': 'lightcoral', 'Registered': 'steelblue'}, order=time_of_day_order)
            axes[0,1].set_title('Rata-rata Penyewaan: Casual vs Registered', fontsize=14)
            axes[0,1].set_xlabel('Segmen Waktu', fontsize=12)
            axes[0,1].set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
            axes[0,1].tick_params(axis='x', rotation=20, ha='right')
            axes[0,1].legend(title="Tipe Pengguna")
            axes[0,1].grid(True, axis='y', linestyle='--', alpha=0.7)

            # 3. Rata-rata Suhu (°C) Aktual per Segmen Waktu
            sns.barplot(x=time_of_day_analysis_df.index, y='avg_temp_actual', data=time_of_day_analysis_df, ax=axes[1,0], palette='Oranges_r', order=time_of_day_order)
            axes[1,0].set_title('Rata-rata Suhu Aktual (°C)', fontsize=14)
            axes[1,0].set_xlabel('Segmen Waktu', fontsize=12)
            axes[1,0].set_ylabel('Rata-rata Suhu (°C)', fontsize=12)
            axes[1,0].tick_params(axis='x', rotation=20, ha='right')
            axes[1,0].grid(True, axis='y', linestyle='--', alpha=0.7)
            
            # 4. Proporsi Kondisi Cuaca per Segmen Waktu
            weather_counts_by_time = adv_analysis_df.groupby(['time_of_day', 'weather_condition']).size().unstack(fill_value=0)
            if not weather_counts_by_time.empty:
                # Reindex kolom weather_condition untuk urutan yang benar
                weather_counts_by_time = weather_counts_by_time.reindex(columns=weather_order, fill_value=0)
                weather_proportions_by_time = weather_counts_by_time.apply(lambda x: x / x.sum() * 100 if x.sum() > 0 else x, axis=1).reindex(time_of_day_order)
                
                weather_proportions_by_time.plot(kind='bar', stacked=True, ax=axes[1,1], colormap='Spectral', width=0.8)
                axes[1,1].set_title('Proporsi Kondisi Cuaca (%)', fontsize=14)
                axes[1,1].set_xlabel('Segmen Waktu', fontsize=12)
                axes[1,1].set_ylabel('Persentase (%)', fontsize=12)
                axes[1,1].tick_params(axis='x', rotation=20, ha='right')
                axes[1,1].legend(title='Kondisi Cuaca', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
                axes[1,1].grid(True, axis='y', linestyle='--', alpha=0.7)
            else:
                axes[1,1].text(0.5, 0.5, 'Tidak ada data proporsi cuaca', horizontalalignment='center', verticalalignment='center', transform=axes[1,1].transAxes)
            
            plt.tight_layout(rect=[0, 0, 1, 0.97]) # Adjust layout untuk judul utama
            st.pyplot(fig_adv)
        else:
            st.info("Tidak ada data yang cukup untuk analisis lanjutan berdasarkan segmen waktu dengan filter saat ini.")
    else:
        st.warning("Tidak ada data atau kolom yang dibutuhkan untuk Analisis Lanjutan berdasarkan filter yang Anda pilih (membutuhkan 'hr', 'cnt_display', 'casual', 'registered', 'temp_actual', 'weather_condition').")


# --- Kesimpulan dan Rekomendasi dari Notebook (di-expander) ---
st.sidebar.markdown("---")
st.sidebar.info("Dashboard ini dibuat berdasarkan analisis dari Proyek Akhir Analisis Data Dicoding.")
st.sidebar.markdown("Nama: Muhammad Husain Fadhlillah")

st.header("📌 Kesimpulan Utama & Rekomendasi Bisnis")
with st.expander("Lihat Detail Kesimpulan dan Rekomendasi Strategis"):
    st.markdown("""
    ### **Jawaban Pertanyaan Bisnis 1: Pola Penggunaan Sepeda**

    Pola penggunaan sepeda sangat dipengaruhi oleh faktor waktu dan kondisi cuaca:

    1.  **Pola Jam Harian:** Terdapat **dua puncak utama (bimodal)**, yaitu pukul **08:00 pagi** (didominasi pengguna *registered* untuk komuting) dan pukul **17:00-18:00 sore** (puncak tertinggi, juga didominasi *registered*). Penggunaan terendah terjadi dini hari (03:00-04:00). Pola ini sedikit berbeda di akhir pekan, dimana penggunaan lebih merata di siang-sore hari.
    2.  **Pola Harian (Mingguan):** Penyewaan cenderung lebih tinggi pada **hari kerja (terutama Kamis dan Jumat)**. Akhir pekan juga menunjukkan aktivitas tinggi, mengindikasikan penggunaan rekreasi.
    3.  **Pola Bulanan & Musiman:** Puncak penggunaan terjadi pada bulan-bulan hangat (**Juni-September**), dengan **Musim Gugur (Fall)** mencatatkan rata-rata penyewaan tertinggi, diikuti Musim Panas. Penggunaan terendah pada Musim Semi (Spring, berdasarkan mapping dataset untuk Januari-Maret).
    4.  **Pengaruh Kondisi Cuaca:**
        * **Cerah/Sedikit Berawan:** Rata-rata penyewaan tertinggi.
        * **Berkabut/Berawan:** Masih cukup tinggi.
        * **Hujan Ringan/Salju Ringan:** Penurunan signifikan.
        * **Hujan Lebat/Salju Lebat/Kabut Tebal:** Penurunan drastis (data terbatas).

    ### **Jawaban Pertanyaan Bisnis 2: Perbedaan Karakteristik Pengguna Casual vs Registered**

    Perbedaan signifikan teridentifikasi antara kedua tipe pengguna:

    1.  **Dominasi Pengguna Registered:** Mencakup **~81.2%** dari total penyewaan, menjadi tulang punggung operasional.
    2.  **Pola Penggunaan Berbeda:**
        * **Registered:** Pola komuting kuat pada hari kerja (puncak pagi & sore). Lebih stabil sepanjang musim, meskipun juga lebih tinggi di musim hangat.
        * **Casual:** Lebih aktif di **akhir pekan dan hari libur** (puncak siang-sore). Proporsi penggunaan lebih tinggi selama musim hangat (Panas & Gugur) dan lebih sensitif terhadap cuaca buruk.
    3.  **Implikasi Strategis:**
        * Fokus pada retensi pengguna *registered*.
        * Strategi untuk akuisisi dan konversi pengguna *casual* menjadi *registered*.

    ### **Analisis Lanjutan (Segmentasi Waktu Penggunaan):**
    * **Pagi (05-10) & Sore (16-20):** Aktivitas tertinggi, didominasi *registered*.
    * **Siang (11-15):** Peningkatan kontribusi *casual*, suhu rata-rata tertinggi.
    * **Malam (21-04):** Aktivitas terendah.

    ---
    ### **💡 Rekomendasi Bisnis Strategis**

    1.  **Optimalisasi Operasional & Penargetan Pengguna:**
        * **Jam Sibuk Komuter (Registered):** Pastikan ketersediaan sepeda di area bisnis/transportasi (07:00-09:00 & 16:00-19:00 Senin-Jumat). Tawarkan paket komuter.
        * **Akhir Pekan & Hari Libur (Casual):** Tingkatkan ketersediaan di area rekreasi (11:00-16:00). Promosikan "Weekend Pass" atau paket keluarga.
        * **Penggunaan Siang Hari (Kerja):** Tawarkan diskon untuk meningkatkan utilisasi (10:00-15:00).

    2.  **Program Loyalitas & Akuisisi:**
        * **Konversi Casual ke Registered:** Insentif diskon registrasi atau akumulasi poin dari sewa casual.
        * **Program Loyalitas Registered:** Tingkatan keanggotaan dengan benefit tambahan (gratis sewa, prioritas).

    3.  **Inisiatif Musiman & Adaptasi Cuaca:**
        * **Promosi Musim Ramai (Gugur & Panas):** Maksimalkan promosi, event tematik.
        * **Strategi Musim Sepi (Semi Awal & Dingin):** Diskon khusus, promosi "Warm Ride".
        * **Mitigasi Cuaca Buruk:** Integrasi prediksi cuaca di aplikasi, "Rain Guarantee" (diskon/gratis sewa berikutnya), sepeda "rain-ready".

    4.  **Penempatan & Alokasi Armada Cerdas:**
        * Gunakan data heatmap (jam vs hari/bulan/musim) untuk optimasi distribusi armada.
        * Analisis proporsi pengguna per stasiun untuk promosi yang lebih tertarget.
    """)

# Menampilkan Data Mentah yang Telah Difilter (opsional, dalam expander)
with st.expander("Tampilkan Data Tabel yang Telah Difilter"):
    st.markdown("#### Data Per Jam (Filtered)")
    if not hour_data_filtered.empty:
        st.dataframe(hour_data_filtered.head())
        st.caption(f"Menampilkan {len(hour_data_filtered)} baris data per jam yang telah difilter.")
    else:
        st.info("Tidak ada data per jam untuk ditampilkan berdasarkan filter yang dipilih.")

    st.markdown("#### Data Harian (Filtered)")
    if not day_data_filtered.empty:
        st.dataframe(day_data_filtered.head())
        st.caption(f"Menampilkan {len(day_data_filtered)} baris data harian yang telah difilter.")
    else:
        st.info("Tidak ada data harian untuk ditampilkan berdasarkan filter yang dipilih.")