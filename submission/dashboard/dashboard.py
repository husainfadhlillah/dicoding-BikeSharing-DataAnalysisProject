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

# --- Fungsi dan Konstanta ---
# Order konstanta untuk plot dan filter
WEEKDAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
MONTH_ORDER = calendar.month_name[1:]
SEASON_ORDER = ['Spring', 'Summer', 'Fall', 'Winter']
WEATHER_ORDER = ['Clear/Few clouds', 'Mist/Cloudy', 'Light Snow/Rain', 'Heavy Rain/Snow/Fog']
TIME_OF_DAY_ORDER = ['Pagi (05-10)', 'Siang (11-15)', 'Sore (16-20)', 'Malam (21-04)']

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
min_date_val = day_df['dteday'].min()
max_date_val = day_df['dteday'].max()

date_range = st.sidebar.date_input(
    "Periode Analisis:",
    value=(min_date_val, max_date_val),
    min_value=min_date_val,
    max_value=max_date_val,
    key="date_filter"
)
start_date, end_date = date_range
if len(date_range) == 1: # Handle kasus saat hanya satu tanggal dipilih
    start_date = date_range[0]
    end_date = max_date_val


# Filter Tahun
unique_years_from_data = sorted(hour_df['year'].unique())
selected_year = st.sidebar.multiselect(
    "Tahun:",
    options=unique_years_from_data,
    default=unique_years_from_data,
    key="year_filter"
)

# Filter Musim
available_seasons_in_order = [s for s in SEASON_ORDER if s in hour_df['season_name'].unique()]
selected_season = st.sidebar.multiselect(
    "Musim:",
    options=available_seasons_in_order,
    default=available_seasons_in_order,
    key="season_filter"
)

# Filter Kondisi Cuaca
available_weather_in_order = [w for w in WEATHER_ORDER if w in hour_df['weather_condition'].unique()]
selected_weather = st.sidebar.multiselect(
    "Kondisi Cuaca:",
    options=available_weather_in_order,
    default=available_weather_in_order,
    key="weather_filter"
)

# Filter Jenis Pengguna
selected_user_type = st.sidebar.radio(
    "Jenis Pengguna:",
    options=['Semua', 'Casual', 'Registered'],
    index=0,
    key="user_type_filter"
)

# --- Proses Filter Data ---
hour_data_filtered = hour_df.copy()
day_data_filtered = day_df.copy()

# Terapkan filter tanggal
if start_date and end_date:
    hour_data_filtered = hour_data_filtered[
        (hour_data_filtered['dteday'] >= pd.to_datetime(start_date)) &
        (hour_data_filtered['dteday'] <= pd.to_datetime(end_date))
    ]
    day_data_filtered = day_data_filtered[
        (day_data_filtered['dteday'] >= pd.to_datetime(start_date)) &
        (day_data_filtered['dteday'] <= pd.to_datetime(end_date))
    ]

# Terapkan filter tahun
if selected_year:
    hour_data_filtered = hour_data_filtered[hour_data_filtered['year'].isin(selected_year)]
    day_data_filtered = day_data_filtered[day_data_filtered['year'].isin(selected_year)]

# Terapkan filter musim
if selected_season:
    hour_data_filtered = hour_data_filtered[hour_data_filtered['season_name'].isin(selected_season)]
    day_data_filtered = day_data_filtered[day_data_filtered['season_name'].isin(selected_season)]

# Terapkan filter kondisi cuaca
if selected_weather:
    hour_data_filtered = hour_data_filtered[hour_data_filtered['weather_condition'].isin(selected_weather)]
    day_data_filtered = day_data_filtered[day_data_filtered['weather_condition'].isin(selected_weather)]


# Tentukan kolom 'cnt_display' berdasarkan filter jenis pengguna
if selected_user_type == 'Casual':
    count_column_to_display = 'casual'
elif selected_user_type == 'Registered':
    count_column_to_display = 'registered'
else: # Semua
    count_column_to_display = 'cnt'

# Pastikan kolom 'cnt_display' ada di kedua dataframe setelah filtering,
# bahkan jika hasilnya kosong, agar plot tidak error
if not hour_data_filtered.empty:
    hour_data_filtered['cnt_display'] = hour_data_filtered[count_column_to_display]
else:
    hour_data_filtered = pd.DataFrame(columns=hour_df.columns.tolist() + ['cnt_display'])

if not day_data_filtered.empty:
    day_data_filtered['cnt_display'] = day_data_filtered[count_column_to_display]
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


with tab1:
    st.header("🕒 Pola Penggunaan Sepeda Berdasarkan Waktu dan Musim")

    if not hour_data_filtered.empty:
        col1a, col1b = st.columns(2)

        with col1a:
            st.subheader("Rata-rata Penyewaan per Jam")
            hourly_pattern = hour_data_filtered.groupby('hr')['cnt_display'].mean().reset_index()
            if not hourly_pattern.empty:
                fig_hr, ax_hr = plt.subplots(figsize=(10, 5))
                sns.lineplot(x='hr', y='cnt_display', data=hourly_pattern, marker='o', linewidth=2, ax=ax_hr, color='dodgerblue')
                ax_hr.set_title('Rata-rata Penyewaan per Jam', fontsize=15)
                ax_hr.set_xlabel('Jam dalam Sehari', fontsize=12)
                ax_hr.set_ylabel(f'Rata-rata Penyewaan ({selected_user_type})', fontsize=12)
                ax_hr.set_xticks(range(0, 24))
                ax_hr.grid(True, linestyle='--', alpha=0.7)
                st.pyplot(fig_hr)
            else:
                st.info("Tidak ada data penyewaan per jam untuk filter yang dipilih.")

            st.subheader("Rata-rata Penyewaan per Musim")
            seasonal_pattern_tab1 = hour_data_filtered.groupby('season_name')['cnt_display'].mean()
            if not seasonal_pattern_tab1.empty:
                seasonal_pattern_tab1 = seasonal_pattern_tab1.reindex(SEASON_ORDER).dropna().reset_index()
                fig_season_t1, ax_season_t1 = plt.subplots(figsize=(10, 5))
                sns.barplot(x='season_name', y='cnt_display', data=seasonal_pattern_tab1, palette='viridis', ax=ax_season_t1)
                ax_season_t1.set_title('Rata-rata Penyewaan per Musim', fontsize=15)
                ax_season_t1.set_xlabel('Musim', fontsize=12)
                ax_season_t1.set_ylabel(f'Rata-rata Penyewaan ({selected_user_type})', fontsize=12)
                ax_season_t1.grid(True, axis='y', linestyle='--', alpha=0.7)
                st.pyplot(fig_season_t1)
            else:
                st.info("Tidak ada data penyewaan per musim untuk filter yang dipilih.")

        with col1b:
            st.subheader("Rata-rata Penyewaan per Hari dalam Seminggu")
            daily_pattern_weekday = hour_data_filtered.groupby('weekday_name')['cnt_display'].mean()
            if not daily_pattern_weekday.empty:
                daily_pattern_weekday = daily_pattern_weekday.reindex(WEEKDAY_ORDER).dropna().reset_index()
                fig_day, ax_day = plt.subplots(figsize=(10, 5))
                sns.barplot(x='weekday_name', y='cnt_display', data=daily_pattern_weekday, palette='crest', ax=ax_day)
                ax_day.set_title('Rata-rata Penyewaan per Hari', fontsize=15)
                ax_day.set_xlabel('Hari', fontsize=12)
                ax_day.set_ylabel(f'Rata-rata Penyewaan ({selected_user_type})', fontsize=12)
                ax_day.tick_params(axis='x', rotation=30)
                ax_day.grid(True, axis='y', linestyle='--', alpha=0.7)
                st.pyplot(fig_day)
            else:
                st.info("Tidak ada data penyewaan per hari untuk filter yang dipilih.")

            st.subheader("Rata-rata Penyewaan per Bulan")
            monthly_pattern = hour_data_filtered.groupby('month_name')['cnt_display'].mean()
            if not monthly_pattern.empty:
                monthly_pattern = monthly_pattern.reindex(MONTH_ORDER).dropna().reset_index()
                fig_month, ax_month = plt.subplots(figsize=(10, 5))
                sns.lineplot(x='month_name', y='cnt_display', data=monthly_pattern, marker='o', linewidth=2, color='mediumseagreen', sort=False, ax=ax_month)
                ax_month.set_title('Rata-rata Penyewaan per Bulan', fontsize=15)
                ax_month.set_xlabel('Bulan', fontsize=12)
                ax_month.set_ylabel(f'Rata-rata Penyewaan ({selected_user_type})', fontsize=12)
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
            if not hour_data_filtered.empty:
                hour_weekday_heatmap_df = hour_data_filtered.pivot_table(index='hr', columns='weekday_name', values='cnt_display', aggfunc='mean')
                if not hour_weekday_heatmap_df.empty:
                    hour_weekday_heatmap_df = hour_weekday_heatmap_df.reindex(columns=[wd for wd in WEEKDAY_ORDER if wd in hour_weekday_heatmap_df.columns])
                    fig_hm_day, ax_hm_day = plt.subplots(figsize=(10, 7))
                    sns.heatmap(hour_weekday_heatmap_df, cmap='viridis', annot=False, fmt=".0f", linewidths=.5,
                                cbar_kws={'label': f'Rata-rata Penyewaan ({selected_user_type})'}, ax=ax_hm_day)
                    ax_hm_day.set_title('Heatmap: Jam vs Hari', fontsize=14)
                    ax_hm_day.set_xlabel('Hari', fontsize=11)
                    ax_hm_day.set_ylabel('Jam', fontsize=11)
                    st.pyplot(fig_hm_day)
                else:
                    st.info("Tidak ada data heatmap jam vs hari untuk filter yang dipilih.")
            else:
                st.info("Data kosong untuk heatmap jam vs hari.")


        with col_hm2:
            st.markdown("##### Jam vs Bulan")
            if not hour_data_filtered.empty:
                hour_month_heatmap_df = hour_data_filtered.pivot_table(index='hr', columns='month_name', values='cnt_display', aggfunc='mean')
                if not hour_month_heatmap_df.empty:
                    hour_month_heatmap_df = hour_month_heatmap_df.reindex(columns=[m for m in MONTH_ORDER if m in hour_month_heatmap_df.columns])
                    fig_hm_month, ax_hm_month = plt.subplots(figsize=(10, 7))
                    sns.heatmap(hour_month_heatmap_df, cmap='YlGnBu', annot=False, fmt=".0f", linewidths=.5,
                                cbar_kws={'label': f'Rata-rata Penyewaan ({selected_user_type})'}, ax=ax_hm_month)
                    ax_hm_month.set_title('Heatmap: Jam vs Bulan', fontsize=14)
                    ax_hm_month.set_xlabel('Bulan', fontsize=11)
                    ax_hm_month.set_ylabel('Jam', fontsize=11)
                    ax_hm_month.tick_params(axis='x', rotation=45, ha='right')
                    st.pyplot(fig_hm_month)
                else:
                    st.info("Tidak ada data heatmap jam vs bulan untuk filter yang dipilih.")
            else:
                st.info("Data kosong untuk heatmap jam vs bulan.")

        st.markdown("---")
        st.markdown("##### Jam vs Musim")
        if not hour_data_filtered.empty:
            hour_season_heatmap_df = hour_data_filtered.pivot_table(index='hr', columns='season_name', values='cnt_display', aggfunc='mean')
            if not hour_season_heatmap_df.empty:
                hour_season_heatmap_df = hour_season_heatmap_df.reindex(columns=[s for s in SEASON_ORDER if s in hour_season_heatmap_df.columns])
                fig_hm_season, ax_hm_season = plt.subplots(figsize=(10, 7)) # Adjusted figure size
                sns.heatmap(hour_season_heatmap_df, cmap='coolwarm', annot=True, fmt=".0f", linewidths=.5,
                        cbar_kws={'label': f'Rata-rata Penyewaan ({selected_user_type})'}, ax=ax_hm_season)
                ax_hm_season.set_title('Heatmap: Jam vs Musim', fontsize=16)
                ax_hm_season.set_xlabel('Musim', fontsize=14)
                ax_hm_season.set_ylabel('Jam dalam Sehari', fontsize=14)
                st.pyplot(fig_hm_season)
            else:
                st.info("Tidak ada data heatmap jam vs musim untuk filter yang dipilih.")
        else:
            st.info("Data kosong untuk heatmap jam vs musim.")

    else:
        st.warning("Tidak ada data untuk ditampilkan di tab Pola Waktu & Musiman berdasarkan filter yang Anda pilih.")


with tab2:
    st.header("☀️ Pengaruh Kondisi Cuaca terhadap Penyewaan")

    if not hour_data_filtered.empty:
        col2a, col2b = st.columns([6, 4])

        with col2a:
            st.subheader("Rata-rata Penyewaan berdasarkan Kondisi Cuaca")
            weather_impact_df = hour_data_filtered.groupby('weather_condition')['cnt_display'].mean()
            if not weather_impact_df.empty:
                weather_impact_df = weather_impact_df.reindex(WEATHER_ORDER).dropna().reset_index()
                fig_weather, ax_weather = plt.subplots(figsize=(10, 6))
                sns.barplot(x='weather_condition', y='cnt_display', data=weather_impact_df, palette='coolwarm', ax=ax_weather)
                ax_weather.set_title('Pengaruh Kondisi Cuaca terhadap Rata-rata Penyewaan', fontsize=15)
                ax_weather.set_xlabel('Kondisi Cuaca', fontsize=12)
                ax_weather.set_ylabel(f'Rata-rata Penyewaan ({selected_user_type})', fontsize=12)
                ax_weather.tick_params(axis='x', rotation=15, ha='right')
                ax_weather.grid(True, axis='y', linestyle='--', alpha=0.7)
                st.pyplot(fig_weather)

                weather_params_df = hour_data_filtered.groupby('weather_condition').agg(
                    avg_temp_actual=('temp_actual', 'mean'),
                    avg_hum_actual=('hum_actual', 'mean')
                ).reindex(WEATHER_ORDER).dropna().reset_index()

                if not weather_params_df.empty:
                    st.markdown("##### Parameter Cuaca Rata-rata per Kondisi:")
                    st.dataframe(weather_params_df.set_index('weather_condition').style.format("{:.2f}"))
                else:
                    st.info("Tidak ada data parameter cuaca untuk filter yang dipilih.")
            else:
                st.info("Tidak ada data dampak cuaca untuk filter yang dipilih.")

        with col2b:
            st.subheader("Distribusi Penyewaan vs Parameter Cuaca")
            if 'temp_actual' in hour_data_filtered.columns:
                fig_scatter_temp, ax_scatter_temp = plt.subplots(figsize=(8,5))
                sns.scatterplot(x='temp_actual', y='cnt_display', data=hour_data_filtered, alpha=0.5, ax=ax_scatter_temp, color='red')
                ax_scatter_temp.set_title(f'Penyewaan ({selected_user_type}) vs Suhu Aktual (°C)', fontsize=14)
                ax_scatter_temp.set_xlabel('Suhu Aktual (°C)', fontsize=11)
                ax_scatter_temp.set_ylabel(f'Jumlah Penyewaan ({selected_user_type})', fontsize=11)
                st.pyplot(fig_scatter_temp)
            else:
                st.info("Kolom suhu aktual tidak tersedia.")

            if 'hum_actual' in hour_data_filtered.columns:
                fig_scatter_hum, ax_scatter_hum = plt.subplots(figsize=(8,5))
                sns.scatterplot(x='hum_actual', y='cnt_display', data=hour_data_filtered, alpha=0.5, ax=ax_scatter_hum, color='blue')
                ax_scatter_hum.set_title(f'Penyewaan ({selected_user_type}) vs Kelembapan Aktual (%)', fontsize=14)
                ax_scatter_hum.set_xlabel('Kelembapan Aktual (%)', fontsize=11)
                ax_scatter_hum.set_ylabel(f'Jumlah Penyewaan ({selected_user_type})', fontsize=11)
                st.pyplot(fig_scatter_hum)
            else:
                st.info("Kolom kelembapan aktual tidak tersedia.")


        st.markdown("---")
        st.subheader("Heatmap Penyewaan: Jam vs Kondisi Cuaca")
        if not hour_data_filtered.empty:
            hour_weather_heatmap_df = hour_data_filtered.pivot_table(index='hr', columns='weather_condition', values='cnt_display', aggfunc='mean')
            if not hour_weather_heatmap_df.empty:
                hour_weather_heatmap_df = hour_weather_heatmap_df.reindex(columns=[w for w in WEATHER_ORDER if w in hour_weather_heatmap_df.columns])
                fig_hm_weather, ax_hm_weather = plt.subplots(figsize=(10, 8))
                sns.heatmap(hour_weather_heatmap_df, cmap='magma_r', annot=True, fmt=".0f", linewidths=.5,
                            cbar_kws={'label': f'Rata-rata Penyewaan ({selected_user_type})'}, ax=ax_hm_weather)
                ax_hm_weather.set_title('Heatmap: Jam vs Kondisi Cuaca', fontsize=16)
                ax_hm_weather.set_xlabel('Kondisi Cuaca', fontsize=12)
                ax_hm_weather.set_ylabel('Jam', fontsize=12)
                ax_hm_weather.tick_params(axis='x', rotation=15, ha='right')
                st.pyplot(fig_hm_weather)
            else:
                st.info("Tidak ada data heatmap jam vs kondisi cuaca untuk filter yang dipilih.")
        else:
            st.info("Data kosong untuk heatmap jam vs kondisi cuaca.")
    else:
        st.warning("Tidak ada data untuk ditampilkan di tab Pengaruh Cuaca berdasarkan filter yang Anda pilih.")


with tab3:
    st.header("👥 Analisis Berdasarkan Jenis Pengguna")

    # Proporsi Pengguna hanya relevan jika 'Semua' jenis pengguna dipilih
    if selected_user_type == "Semua" and not day_data_filtered.empty and 'casual' in day_data_filtered and 'registered' in day_data_filtered:
        st.subheader("Proporsi Pengguna Casual vs Registered (Periode Terfilter)")
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
    elif selected_user_type != "Semua":
        st.info(f"Menampilkan data spesifik untuk pengguna {selected_user_type}. Diagram proporsi keseluruhan tidak ditampilkan.")
    else:
        st.info("Data harian tidak cukup atau kolom casual/registered tidak ada untuk menampilkan proporsi pengguna.")

    st.markdown("---")

    if not hour_data_filtered.empty and 'casual' in hour_data_filtered and 'registered' in hour_data_filtered:
        # Grafik perbandingan hanya jika 'Semua' pengguna dipilih
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
                    user_type_season_df = user_type_season_df.reindex(SEASON_ORDER).dropna().reset_index()
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
        elif selected_user_type != "Semua" and not hour_data_filtered.empty:
            st.subheader(f"Pola Penggunaan untuk Pengguna {selected_user_type} (berdasarkan 'cnt_display')")
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
        st.warning("Tidak ada data untuk ditampilkan di tab Analisis Pengguna berdasarkan filter yang Anda pilih.")



with tab4:
    st.header("🔬 Analisis Lanjutan: Segmentasi Pengguna Berdasarkan Waktu Penggunaan Harian")
    st.markdown("""
    Analisis ini mengelompokkan jam dalam sehari menjadi empat segmen waktu untuk memahami karakteristik penggunaan sepeda lebih detail pada setiap segmen.
    """)

    if not hour_data_filtered.empty:
        # Fungsi untuk Manual Grouping berdasarkan waktu
        def assign_time_of_day(hr_val):
            if 5 <= hr_val <= 10: return 'Pagi (05-10)'
            elif 11 <= hr_val <= 15: return 'Siang (11-15)'
            elif 16 <= hr_val <= 20: return 'Sore (16-20)'
            else: return 'Malam (21-04)'

        adv_analysis_df = hour_data_filtered.copy()
        adv_analysis_df['time_of_day'] = adv_analysis_df['hr'].apply(assign_time_of_day)

        time_of_day_analysis_df = adv_analysis_df.groupby('time_of_day').agg(
            avg_total_users=('cnt_display', 'mean'), # Menggunakan cnt_display untuk konsistensi dengan filter
            avg_casual_users=('casual', 'mean'),
            avg_registered_users=('registered', 'mean'),
            avg_temp_actual=('temp_actual', 'mean')
        ).reindex(TIME_OF_DAY_ORDER).dropna(how='all') # Hapus baris jika semua NaN

        if not time_of_day_analysis_df.empty:
            fig_adv, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig_adv.suptitle(f'Karakteristik Penyewaan Sepeda per Segmen Waktu Harian ({selected_user_type})', fontsize=18, y=1.02)

            # 1. Rata-rata Total Penyewaan per Segmen Waktu
            sns.barplot(x=time_of_day_analysis_df.index, y='avg_total_users', data=time_of_day_analysis_df, ax=axes[0,0], palette='Blues_r')
            axes[0,0].set_title('Rata-rata Total Penyewaan', fontsize=14)
            axes[0,0].set_xlabel('Segmen Waktu', fontsize=12)
            axes[0,0].set_ylabel(f'Rata-rata Penyewaan ({selected_user_type})', fontsize=12)
            axes[0,0].tick_params(axis='x', rotation=20, ha='right')
            axes[0,0].grid(True, axis='y', linestyle='--', alpha=0.7)

            # 2. Rata-rata Pengguna Casual vs Registered per Segmen Waktu (Hanya jika 'Semua' dipilih)
            if selected_user_type == "Semua":
                time_of_day_melted_adv = time_of_day_analysis_df[['avg_casual_users', 'avg_registered_users']].reset_index().melt(id_vars='time_of_day', var_name='user_type', value_name='avg_users')
                time_of_day_melted_adv['user_type'] = time_of_day_melted_adv['user_type'].map({'avg_casual_users':'Casual', 'avg_registered_users':'Registered'})
                sns.barplot(x='time_of_day', y='avg_users', hue='user_type', data=time_of_day_melted_adv, ax=axes[0,1],
                            palette={'Casual': 'lightcoral', 'Registered': 'steelblue'}, order=TIME_OF_DAY_ORDER)
                axes[0,1].set_title('Rata-rata Penyewaan: Casual vs Registered', fontsize=14)
            else:
                axes[0,1].text(0.5, 0.5, f'Menampilkan data untuk\n{selected_user_type}', horizontalalignment='center', verticalalignment='center', transform=axes[0,1].transAxes, fontsize=12)
                axes[0,1].set_title('Rata-rata Penyewaan per Tipe Pengguna', fontsize=14)

            axes[0,1].set_xlabel('Segmen Waktu', fontsize=12)
            axes[0,1].set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
            axes[0,1].tick_params(axis='x', rotation=20, ha='right')
            axes[0,1].legend(title="Tipe Pengguna")
            axes[0,1].grid(True, axis='y', linestyle='--', alpha=0.7)


            # 3. Rata-rata Suhu (°C) Aktual per Segmen Waktu
            sns.barplot(x=time_of_day_analysis_df.index, y='avg_temp_actual', data=time_of_day_analysis_df, ax=axes[1,0], palette='Oranges_r')
            axes[1,0].set_title('Rata-rata Suhu Aktual (°C)', fontsize=14)
            axes[1,0].set_xlabel('Segmen Waktu', fontsize=12)
            axes[1,0].set_ylabel('Rata-rata Suhu (°C)', fontsize=12)
            axes[1,0].tick_params(axis='x', rotation=20, ha='right')
            axes[1,0].grid(True, axis='y', linestyle='--', alpha=0.7)

            # 4. Proporsi Kondisi Cuaca per Segmen Waktu
            weather_counts_by_time = adv_analysis_df.groupby(['time_of_day', 'weather_condition']).size().unstack(fill_value=0)
            if not weather_counts_by_time.empty:
                weather_counts_by_time = weather_counts_by_time.reindex(columns=[w for w in WEATHER_ORDER if w in weather_counts_by_time.columns], fill_value=0)
                weather_proportions_by_time = weather_counts_by_time.apply(lambda x: x / x.sum() * 100 if x.sum() > 0 else x, axis=1).reindex(TIME_OF_DAY_ORDER).dropna(how='all')

                if not weather_proportions_by_time.empty:
                    weather_proportions_by_time.plot(kind='bar', stacked=True, ax=axes[1,1], colormap='Spectral', width=0.8)
                    axes[1,1].set_title('Proporsi Kondisi Cuaca (%)', fontsize=14)
                    axes[1,1].set_xlabel('Segmen Waktu', fontsize=12)
                    axes[1,1].set_ylabel('Persentase (%)', fontsize=12)
                    axes[1,1].tick_params(axis='x', rotation=20, ha='right')
                    axes[1,1].legend(title='Kondisi Cuaca', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
                    axes[1,1].grid(True, axis='y', linestyle='--', alpha=0.7)
                else:
                     axes[1,1].text(0.5, 0.5, 'Tidak ada data proporsi cuaca', horizontalalignment='center', verticalalignment='center', transform=axes[1,1].transAxes)
            else:
                axes[1,1].text(0.5, 0.5, 'Tidak ada data proporsi cuaca', horizontalalignment='center', verticalalignment='center', transform=axes[1,1].transAxes)

            plt.tight_layout(rect=[0, 0, 1, 0.97])
            st.pyplot(fig_adv)
        else:
            st.info("Tidak ada data yang cukup untuk analisis lanjutan berdasarkan segmen waktu dengan filter saat ini.")
    else:
        st.warning("Tidak ada data atau kolom yang dibutuhkan untuk Analisis Lanjutan berdasarkan filter yang Anda pilih.")


# --- Kesimpulan dan Rekomendasi ---
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

# Menampilkan Data Mentah yang Telah Difilter
with st.expander("Tampilkan Data Tabel yang Telah Difilter"):
    st.markdown("#### Data Per Jam (Filtered)")
    if not hour_data_filtered.empty:
        st.dataframe(hour_data_filtered[['dteday', 'season_name', 'year', 'month_name', 'hr', 'weekday_name', 'weather_condition', 'temp_actual', 'hum_actual', 'casual', 'registered', 'cnt_display']].head())
        st.caption(f"Menampilkan {len(hour_data_filtered)} baris data per jam yang telah difilter.")
    else:
        st.info("Tidak ada data per jam untuk ditampilkan berdasarkan filter yang dipilih.")

    st.markdown("#### Data Harian (Filtered)")
    if not day_data_filtered.empty:
        st.dataframe(day_data_filtered[['dteday', 'season_name', 'year', 'month_name', 'weekday_name', 'weather_condition', 'temp_actual', 'hum_actual', 'casual', 'registered', 'cnt_display']].head())
        st.caption(f"Menampilkan {len(day_data_filtered)} baris data harian yang telah difilter.")
    else:
        st.info("Tidak ada data harian untuk ditampilkan berdasarkan filter yang dipilih.")