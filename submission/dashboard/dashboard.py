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
MONTH_ORDER = calendar.month_name[1:] # January to December
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
if not hour_df.empty and not day_df.empty:
    st.sidebar.header("⚙️ Filter Data Interaktif")

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
    if len(date_range) == 1:
        start_date = date_range[0]
        end_date = max_date_val

    unique_years_from_data = sorted(hour_df['year'].unique())
    selected_year = st.sidebar.multiselect(
        "Tahun:", options=unique_years_from_data, default=unique_years_from_data, key="year_filter"
    )

    available_seasons_in_order = [s for s in SEASON_ORDER if s in hour_df['season_name'].unique()]
    selected_season = st.sidebar.multiselect(
        "Musim:", options=available_seasons_in_order, default=available_seasons_in_order, key="season_filter"
    )

    available_weather_in_order = [w for w in WEATHER_ORDER if w in hour_df['weather_condition'].unique()]
    selected_weather = st.sidebar.multiselect(
        "Kondisi Cuaca:", options=available_weather_in_order, default=available_weather_in_order, key="weather_filter"
    )

    selected_user_type = st.sidebar.radio(
        "Jenis Pengguna:", options=['Semua', 'Casual', 'Registered'], index=0, key="user_type_filter"
    )

    # --- Proses Filter Data ---
    hour_data_filtered = hour_df.copy()
    day_data_filtered = day_df.copy()

    if start_date and end_date:
        hour_data_filtered = hour_data_filtered[
            (hour_data_filtered['dteday'] >= pd.to_datetime(start_date)) &
            (hour_data_filtered['dteday'] <= pd.to_datetime(end_date))
        ]
        day_data_filtered = day_data_filtered[
            (day_data_filtered['dteday'] >= pd.to_datetime(start_date)) &
            (day_data_filtered['dteday'] <= pd.to_datetime(end_date))
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

    count_column_to_display = 'cnt'
    if selected_user_type == 'Casual':
        count_column_to_display = 'casual'
    elif selected_user_type == 'Registered':
        count_column_to_display = 'registered'

    if not hour_data_filtered.empty:
        hour_data_filtered['cnt_display'] = hour_data_filtered[count_column_to_display]
    else:
        hour_data_filtered = pd.DataFrame(columns=hour_df.columns.tolist() + ['cnt_display'])
    if not day_data_filtered.empty:
        day_data_filtered['cnt_display'] = day_data_filtered[count_column_to_display]
    else:
        day_data_filtered = pd.DataFrame(columns=day_df.columns.tolist() + ['cnt_display'])

else: # Jika data awal gagal dimuat
    st.error("Gagal memuat data awal. Tidak dapat menampilkan dashboard.")
    st.stop() # Menghentikan eksekusi skrip lebih lanjut


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
            st.subheader("Pola Penggunaan Sepeda Berdasarkan Jam")
            hourly_pattern = hour_data_filtered.groupby('hr')['cnt_display'].mean().reset_index()
            if not hourly_pattern.empty:
                fig_hr, ax_hr = plt.subplots(figsize=(10, 5))
                sns.lineplot(x='hr', y='cnt_display', data=hourly_pattern, marker='o', linewidth=2, ax=ax_hr, color='dodgerblue')
                ax_hr.set_title('Rata-rata Penyewaan Sepeda berdasarkan Jam', fontsize=15)
                ax_hr.set_xlabel('Jam dalam Sehari', fontsize=12)
                ax_hr.set_ylabel(f'Rata-rata Penyewaan ({selected_user_type})', fontsize=12)
                ax_hr.set_xticks(range(0, 24))
                ax_hr.grid(True, linestyle='--', alpha=0.7)
                st.pyplot(fig_hr)
            else: st.info("Tidak ada data penyewaan per jam untuk filter yang dipilih.")

            st.subheader("Pola Penggunaan Sepeda Berdasarkan Musim")
            seasonal_pattern_tab1 = hour_data_filtered.groupby('season_name')['cnt_display'].mean()
            if not seasonal_pattern_tab1.empty:
                seasonal_pattern_tab1 = seasonal_pattern_tab1.reindex(SEASON_ORDER).dropna().reset_index()
                if not seasonal_pattern_tab1.empty: # Check again after reindex
                    fig_season_t1, ax_season_t1 = plt.subplots(figsize=(10, 5))
                    sns.barplot(x='season_name', y='cnt_display', data=seasonal_pattern_tab1, palette='viridis', ax=ax_season_t1, order=[s for s in SEASON_ORDER if s in seasonal_pattern_tab1['season_name'].values])
                    ax_season_t1.set_title('Rata-rata Penyewaan Sepeda berdasarkan Musim', fontsize=15)
                    ax_season_t1.set_xlabel('Musim', fontsize=12)
                    ax_season_t1.set_ylabel(f'Rata-rata Penyewaan ({selected_user_type})', fontsize=12)
                    ax_season_t1.grid(True, axis='y', linestyle='--', alpha=0.7)
                    st.pyplot(fig_season_t1)
                else: st.info("Tidak ada data penyewaan per musim yang valid setelah reindex.")
            else: st.info("Tidak ada data penyewaan per musim untuk filter yang dipilih.")
        with col1b:
            st.subheader("Pola Penggunaan Sepeda Berdasarkan Hari dalam Seminggu")
            daily_pattern_weekday = hour_data_filtered.groupby('weekday_name')['cnt_display'].mean()
            if not daily_pattern_weekday.empty:
                daily_pattern_weekday = daily_pattern_weekday.reindex(WEEKDAY_ORDER).dropna().reset_index()
                if not daily_pattern_weekday.empty:
                    fig_day, ax_day = plt.subplots(figsize=(10, 5))
                    sns.barplot(x='weekday_name', y='cnt_display', data=daily_pattern_weekday, palette='crest', ax=ax_day, order=[wd for wd in WEEKDAY_ORDER if wd in daily_pattern_weekday['weekday_name'].values])
                    ax_day.set_title('Rata-rata Penyewaan Sepeda berdasarkan Hari dalam Seminggu', fontsize=15)
                    ax_day.set_xlabel('Hari', fontsize=12)
                    ax_day.set_ylabel(f'Rata-rata Penyewaan ({selected_user_type})', fontsize=12)
                    plt.setp(ax_day.get_xticklabels(), rotation=30, ha="right")
                    ax_day.grid(True, axis='y', linestyle='--', alpha=0.7)
                    st.pyplot(fig_day)
                else: st.info("Tidak ada data penyewaan per hari yang valid setelah reindex.")
            else: st.info("Tidak ada data penyewaan per hari untuk filter yang dipilih.")

            st.subheader("Pola Penggunaan Sepeda Berdasarkan Bulan")
            monthly_pattern = hour_data_filtered.groupby('month_name')['cnt_display'].mean()
            if not monthly_pattern.empty:
                monthly_pattern = monthly_pattern.reindex(MONTH_ORDER).dropna().reset_index()
                if not monthly_pattern.empty:
                    fig_month, ax_month = plt.subplots(figsize=(10, 5))
                    sns.lineplot(x='month_name', y='cnt_display', data=monthly_pattern, marker='o', linewidth=2, color='mediumseagreen', sort=False, ax=ax_month)
                    ax_month.set_title('Rata-rata Penyewaan Sepeda berdasarkan Bulan', fontsize=15)
                    ax_month.set_xlabel('Bulan', fontsize=12)
                    ax_month.set_ylabel(f'Rata-rata Penyewaan ({selected_user_type})', fontsize=12)
                    plt.setp(ax_month.get_xticklabels(), rotation=45, ha="right")
                    ax_month.grid(True, linestyle='--', alpha=0.7)
                    st.pyplot(fig_month)
                else: st.info("Tidak ada data penyewaan per bulan yang valid setelah reindex.")
            else: st.info("Tidak ada data penyewaan per bulan untuk filter yang dipilih.")

        st.markdown("---")
        st.subheader("Heatmap Pola Penyewaan")
        col_hm1, col_hm2 = st.columns(2)
        with col_hm1:
            st.markdown("##### Jam vs Hari dalam Seminggu")
            if not hour_data_filtered.empty:
                hour_weekday_heatmap_df = hour_data_filtered.pivot_table(index='hr', columns='weekday_name', values='cnt_display', aggfunc='mean')
                if not hour_weekday_heatmap_df.empty and not hour_weekday_heatmap_df.isnull().all().all():
                    ordered_weekdays = [wd for wd in WEEKDAY_ORDER if wd in hour_weekday_heatmap_df.columns]
                    if ordered_weekdays:
                        df_to_plot = hour_weekday_heatmap_df.reindex(columns=ordered_weekdays)
                        if not df_to_plot.empty and not df_to_plot.isnull().all().all():
                            fig_hm_day, ax_hm_day = plt.subplots(figsize=(10, 7))
                            sns.heatmap(df_to_plot, cmap='viridis', annot=False, fmt=".0f", linewidths=.5, cbar_kws={'label': f'Rata-rata Penyewaan ({selected_user_type})'}, ax=ax_hm_day)
                            ax_hm_day.set_title('Heatmap Rata-rata Penyewaan Sepeda: Jam vs Hari dalam Seminggu', fontsize=14)
                            ax_hm_day.set_xlabel('Hari dalam Seminggu', fontsize=11); ax_hm_day.set_ylabel('Hari dalam Seminggu', fontsize=11)
                            st.pyplot(fig_hm_day)
                        else: st.info("Tidak ada data heatmap jam vs hari yang valid untuk filter (setelah reindex).")
                    else: st.info("Tidak ada kolom hari yang relevan dalam data pivot heatmap jam vs hari.")
                else: st.info("Tidak ada data heatmap jam vs hari (pivot kosong atau semua NaN).")
            else: st.info("Data utama kosong untuk heatmap jam vs hari.")
        with col_hm2:
            st.markdown("##### Jam vs Bulan")
            if not hour_data_filtered.empty:
                hour_month_heatmap_df = hour_data_filtered.pivot_table(index='hr', columns='month_name', values='cnt_display', aggfunc='mean')
                if not hour_month_heatmap_df.empty and not hour_month_heatmap_df.isnull().all().all():
                    ordered_months = [m for m in MONTH_ORDER if m in hour_month_heatmap_df.columns]
                    if ordered_months:
                        df_to_plot = hour_month_heatmap_df.reindex(columns=ordered_months)
                        if not df_to_plot.empty and not df_to_plot.isnull().all().all():
                            fig_hm_month, ax_hm_month = plt.subplots(figsize=(12, 7))
                            sns.heatmap(df_to_plot, cmap='YlGnBu', annot=False, fmt=".0f", linewidths=.5, cbar_kws={'label': f'Rata-rata Penyewaan ({selected_user_type})'}, ax=ax_hm_month)
                            ax_hm_month.set_title('Heatmap Rata-rata Penyewaan Sepeda: Jam vs Bulan', fontsize=14)
                            ax_hm_month.set_xlabel('Bulan', fontsize=11); ax_hm_month.set_ylabel('Jam dalam Sehari', fontsize=11)
                            plt.setp(ax_hm_month.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
                            st.pyplot(fig_hm_month)
                        else: st.info("Tidak ada data heatmap jam vs bulan yang valid untuk filter (setelah reindex).")
                    else: st.info("Tidak ada kolom bulan yang relevan dalam data pivot heatmap jam vs bulan.")
                else: st.info("Tidak ada data heatmap jam vs bulan (pivot kosong atau semua NaN).")
            else: st.info("Data utama kosong untuk heatmap jam vs bulan.")

        st.markdown("---")
        st.markdown("##### Jam vs Musim")
        if not hour_data_filtered.empty:
            hour_season_heatmap_df = hour_data_filtered.pivot_table(index='hr', columns='season_name', values='cnt_display', aggfunc='mean')
            if not hour_season_heatmap_df.empty and not hour_season_heatmap_df.isnull().all().all():
                ordered_seasons = [s for s in SEASON_ORDER if s in hour_season_heatmap_df.columns]
                if ordered_seasons:
                    df_to_plot = hour_season_heatmap_df.reindex(columns=ordered_seasons)
                    if not df_to_plot.empty and not df_to_plot.isnull().all().all():
                        fig_hm_season, ax_hm_season = plt.subplots(figsize=(10, 7))
                        sns.heatmap(df_to_plot, cmap='coolwarm', annot=True, fmt=".0f", linewidths=.5, cbar_kws={'label': f'Rata-rata Penyewaan ({selected_user_type})'}, ax=ax_hm_season)
                        ax_hm_season.set_title('Heatmap Rata-rata Penyewaan Sepeda: Jam vs Musim', fontsize=16)
                        ax_hm_season.set_xlabel('Musim', fontsize=14); ax_hm_season.set_ylabel('Jam dalam Sehari', fontsize=14)
                        st.pyplot(fig_hm_season)
                    else: st.info("Tidak ada data heatmap jam vs musim yang valid (setelah reindex).")
                else: st.info("Tidak ada kolom musim yang relevan dalam data pivot heatmap jam vs musim.")
            else: st.info("Tidak ada data heatmap jam vs musim (pivot kosong atau semua NaN).")
        else: st.info("Data utama kosong untuk heatmap jam vs musim.")
    else:
        st.warning("Tidak ada data untuk ditampilkan di tab Pola Waktu & Musiman berdasarkan filter Anda.")

with tab2:
    st.header("☀️ Pengaruh Kondisi Cuaca terhadap Penyewaan")
    if not hour_data_filtered.empty:
        col2a, col2b = st.columns([6, 4])
        with col2a:
            st.subheader("Rata-rata Penyewaan berdasarkan Kondisi Cuaca")
            weather_impact_df = hour_data_filtered.groupby('weather_condition')['cnt_display'].mean()
            if not weather_impact_df.empty:
                weather_impact_df = weather_impact_df.reindex(WEATHER_ORDER).dropna().reset_index()
                if not weather_impact_df.empty:
                    fig_weather, ax_weather = plt.subplots(figsize=(10, 6))
                    sns.barplot(x='weather_condition', y='cnt_display', data=weather_impact_df, palette='coolwarm', ax=ax_weather, order=[w for w in WEATHER_ORDER if w in weather_impact_df['weather_condition'].values])
                    ax_weather.set_title('Pengaruh Kondisi Cuaca terhadap Rata-rata Penyewaan', fontsize=15)
                    ax_weather.set_xlabel('Kondisi Cuaca', fontsize=12)
                    ax_weather.set_ylabel(f'Rata-rata Penyewaan ({selected_user_type})', fontsize=12)
                    plt.setp(ax_weather.get_xticklabels(), rotation=15, ha="right", rotation_mode="anchor")
                    ax_weather.grid(True, axis='y', linestyle='--', alpha=0.7)
                    st.pyplot(fig_weather)

                    weather_params_df = hour_data_filtered.groupby('weather_condition').agg(avg_temp_actual=('temp_actual', 'mean'), avg_hum_actual=('hum_actual', 'mean')).reindex(WEATHER_ORDER).dropna().reset_index()
                    if not weather_params_df.empty:
                        st.markdown("##### Parameter Cuaca Rata-rata per Kondisi:")
                        st.dataframe(weather_params_df.set_index('weather_condition').style.format("{:.2f}"))
                else: st.info("Tidak ada data dampak cuaca yang valid setelah reindex.")
            else: st.info("Tidak ada data dampak cuaca untuk filter yang dipilih.")

        st.markdown("---")
        st.subheader("Heatmap Penyewaan: Jam vs Kondisi Cuaca")
        if not hour_data_filtered.empty:
            hour_weather_heatmap_df = hour_data_filtered.pivot_table(index='hr', columns='weather_condition', values='cnt_display', aggfunc='mean')
            if not hour_weather_heatmap_df.empty and not hour_weather_heatmap_df.isnull().all().all():
                ordered_weather_cols = [w for w in WEATHER_ORDER if w in hour_weather_heatmap_df.columns]
                if ordered_weather_cols:
                    df_to_plot = hour_weather_heatmap_df.reindex(columns=ordered_weather_cols)
                    if not df_to_plot.empty and not df_to_plot.isnull().all().all():
                        fig_hm_weather, ax_hm_weather = plt.subplots(figsize=(10, 8))
                        sns.heatmap(df_to_plot, cmap='magma_r', annot=True, fmt=".0f", linewidths=.5, cbar_kws={'label': f'Rata-rata Penyewaan ({selected_user_type})'}, ax=ax_hm_weather)
                        ax_hm_weather.set_title('Heatmap Rata-rata Penyewaan Sepeda: Jam vs Kondisi Cuaca', fontsize=16)
                        ax_hm_weather.set_xlabel('Kondisi Cuaca', fontsize=12); ax_hm_weather.set_ylabel('Jam dalam Sehari', fontsize=12)
                        plt.setp(ax_hm_weather.get_xticklabels(), rotation=15, ha="right", rotation_mode="anchor")
                        st.pyplot(fig_hm_weather)
                    else: st.info("Tidak ada data heatmap jam vs cuaca yang valid (setelah reindex).")
                else: st.info("Tidak ada kolom kondisi cuaca yang relevan dalam data pivot heatmap jam vs cuaca.")
            else: st.info("Tidak ada data heatmap jam vs kondisi cuaca (pivot kosong atau semua NaN).")
        else: st.info("Data utama kosong untuk heatmap jam vs kondisi cuaca.")
    else:
        st.warning("Tidak ada data untuk ditampilkan di tab Pengaruh Cuaca berdasarkan filter Anda.")

with tab3:
    st.header("👥 Analisis Berdasarkan Jenis Pengguna")
    if selected_user_type == "Semua" and not day_data_filtered.empty and 'casual' in day_data_filtered and 'registered' in day_data_filtered:
        st.subheader("Proporsi Pengguna Casual vs Registered (Periode Terfilter)")
        total_users_pie_data = day_data_filtered[['casual', 'registered']].sum()
        if total_users_pie_data.sum() > 0:
            fig_pie_users, ax_pie_users = plt.subplots(figsize=(8, 5))
            ax_pie_users.pie(total_users_pie_data, labels=['Casual', 'Registered'], autopct='%1.1f%%', startangle=140, colors=['#ff9999','#66b3ff'], wedgeprops={'edgecolor': 'grey'})
            ax_pie_users.set_title('Proporsi Total Penyewaan: Casual vs Registered', fontsize=15)
            ax_pie_users.axis('equal')
            st.pyplot(fig_pie_users)
        else: st.info("Tidak ada data penyewaan untuk diagram proporsi.")
    elif selected_user_type != "Semua":
        st.info(f"Menampilkan data spesifik untuk pengguna {selected_user_type}. Diagram proporsi keseluruhan tidak ditampilkan.")
    else: st.info("Data harian tidak cukup atau kolom casual/registered tidak ada untuk menampilkan proporsi pengguna.")

    st.markdown("---")
    if not hour_data_filtered.empty and 'casual' in hour_data_filtered and 'registered' in hour_data_filtered:
        if selected_user_type == "Semua":
            st.subheader("Perbandingan Pola Penggunaan: Casual vs Registered")
            col3a, col3b = st.columns(2)
            with col3a:
                st.markdown("##### Berdasarkan Jam")
                user_type_hourly_df = hour_data_filtered.groupby('hr').agg(avg_casual=('casual', 'mean'), avg_registered=('registered', 'mean')).reset_index()
                if not user_type_hourly_df.empty:
                    fig_user_hr, ax_user_hr = plt.subplots(figsize=(10,5))
                    ax_user_hr.plot(user_type_hourly_df['hr'], user_type_hourly_df['avg_casual'], label='Casual', marker='o', color='skyblue', linewidth=2)
                    ax_user_hr.plot(user_type_hourly_df['hr'], user_type_hourly_df['avg_registered'], label='Registered', marker='x', color='darkblue', linewidth=2)
                    ax_user_hr.set_title('Rata-rata Penyewaan per Jam', fontsize=14); ax_user_hr.set_xlabel('Jam', fontsize=11); ax_user_hr.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=11)
                    ax_user_hr.set_xticks(range(0,24,2)); ax_user_hr.legend(); ax_user_hr.grid(True, linestyle='--', alpha=0.7)
                    st.pyplot(fig_user_hr)
                else: st.info("Tidak ada data perbandingan pengguna per jam.")

                st.markdown("##### Berdasarkan Hari Kerja vs Akhir Pekan/Libur")
                workday_agg_df = hour_data_filtered.groupby('workingday').agg(avg_casual=('casual', 'mean'),avg_registered=('registered', 'mean')).reset_index()
                if not workday_agg_df.empty:
                    workday_agg_df['workingday_label'] = workday_agg_df['workingday'].map({0: 'Akhir Pekan/Libur', 1: 'Hari Kerja'})
                    workday_melted = workday_agg_df.melt(id_vars='workingday_label', value_vars=['avg_casual', 'avg_registered'], var_name='tipe_pengguna', value_name='rata_penyewaan')
                    workday_melted['tipe_pengguna'] = workday_melted['tipe_pengguna'].map({'avg_casual': 'Casual', 'avg_registered': 'Registered'})
                    if not workday_melted.empty:
                        fig_workday, ax_workday = plt.subplots(figsize=(8, 5))
                        sns.barplot(x='workingday_label', y='rata_penyewaan', hue='tipe_pengguna', data=workday_melted, palette={'Casual': 'skyblue', 'Registered': 'darkblue'}, ax=ax_workday)
                        ax_workday.set_title('Penyewaan di Hari Kerja vs Akhir Pekan', fontsize=14); ax_workday.set_xlabel('Status Hari', fontsize=11); ax_workday.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=11); ax_workday.legend(title="Tipe Pengguna")
                        st.pyplot(fig_workday)
                    else: st.info("Tidak ada data perbandingan pengguna berdasarkan status hari (setelah diolah).")
                else: st.info("Tidak ada data perbandingan pengguna berdasarkan status hari.")
            with col3b:
                st.markdown("##### Berdasarkan Musim")
                user_type_season_df = hour_data_filtered.groupby('season_name').agg(avg_casual=('casual', 'mean'),avg_registered=('registered', 'mean'))
                if not user_type_season_df.empty:
                    user_type_season_df = user_type_season_df.reindex(SEASON_ORDER).dropna().reset_index()
                    if not user_type_season_df.empty:
                        user_type_season_melted = user_type_season_df.melt(id_vars='season_name', value_vars=['avg_casual', 'avg_registered'], var_name='tipe_pengguna', value_name='rata_penyewaan')
                        user_type_season_melted['tipe_pengguna'] = user_type_season_melted['tipe_pengguna'].map({'avg_casual': 'Casual', 'avg_registered': 'Registered'})
                        if not user_type_season_melted.empty:
                            fig_user_season, ax_user_season = plt.subplots(figsize=(10,5))
                            sns.barplot(x='season_name', y='rata_penyewaan', hue='tipe_pengguna', data=user_type_season_melted, palette={'Casual': 'skyblue', 'Registered': 'darkblue'}, ax=ax_user_season, order=[s for s in SEASON_ORDER if s in user_type_season_melted['season_name'].values])
                            ax_user_season.set_title('Rata-rata Penyewaan per Musim', fontsize=14); ax_user_season.set_xlabel('Musim', fontsize=11); ax_user_season.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=11); ax_user_season.legend(title="Tipe Pengguna")
                            st.pyplot(fig_user_season)
                        else: st.info("Tidak ada data perbandingan pengguna per musim (setelah diolah).")
                    else: st.info("Tidak ada data perbandingan pengguna per musim (setelah reindex).")
                else: st.info("Tidak ada data perbandingan pengguna per musim.")
        elif selected_user_type != "Semua" and not hour_data_filtered.empty:
            st.subheader(f"Pola Penggunaan untuk Pengguna {selected_user_type}")
            user_specific_hourly = hour_data_filtered.groupby('hr')['cnt_display'].mean().reset_index()
            if not user_specific_hourly.empty:
                fig_user_spec_hr, ax_user_spec_hr = plt.subplots(figsize=(10,5))
                sns.lineplot(x='hr', y='cnt_display', data=user_specific_hourly, marker='o', ax=ax_user_spec_hr, label=selected_user_type)
                ax_user_spec_hr.set_title(f'Rata-rata Penyewaan per Jam ({selected_user_type})', fontsize=14); ax_user_spec_hr.set_xlabel('Jam', fontsize=11); ax_user_spec_hr.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=11); ax_user_spec_hr.legend(); ax_user_spec_hr.grid(True, linestyle='--', alpha=0.7)
                st.pyplot(fig_user_spec_hr)
            else: st.info(f"Tidak ada data pola per jam untuk pengguna {selected_user_type} dengan filter saat ini.")
    else:
        st.warning("Tidak ada data untuk ditampilkan di tab Analisis Pengguna berdasarkan filter Anda.")

with tab4:
    st.header("🔬 Analisis Lanjutan: Segmentasi Pengguna Berdasarkan Waktu Penggunaan Harian")
    st.markdown("Analisis ini mengelompokkan jam dalam sehari menjadi empat segmen waktu...")
    if not hour_data_filtered.empty and not hour_data_filtered[['hr', 'cnt_display', 'casual', 'registered', 'temp_actual', 'weather_condition']].isnull().all().all():
        def assign_time_of_day(hr_val):
            if 5 <= hr_val <= 10: return 'Pagi (05-10)'
            elif 11 <= hr_val <= 15: return 'Siang (11-15)'
            elif 16 <= hr_val <= 20: return 'Sore (16-20)'
            else: return 'Malam (21-04)'
        adv_analysis_df = hour_data_filtered.copy()
        adv_analysis_df['time_of_day'] = adv_analysis_df['hr'].apply(assign_time_of_day)

        time_of_day_analysis_df = adv_analysis_df.groupby('time_of_day').agg(
            avg_total_users=('cnt_display', 'mean'), avg_casual_users=('casual', 'mean'),
            avg_registered_users=('registered', 'mean'), avg_temp_actual=('temp_actual', 'mean')
        ).reindex(TIME_OF_DAY_ORDER).dropna(how='all')

        if not time_of_day_analysis_df.empty:
            fig_adv, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig_adv.suptitle(f'Karakteristik Penyewaan Sepeda per Segmen Waktu Harian ({selected_user_type})', fontsize=18, y=1.02)

            sns.barplot(x=time_of_day_analysis_df.index, y='avg_total_users', data=time_of_day_analysis_df, ax=axes[0,0], palette='Blues_r', order=[t for t in TIME_OF_DAY_ORDER if t in time_of_day_analysis_df.index])
            axes[0,0].set_title('Rata-rata Total Penyewaan per Segmen Waktu', fontsize=14); axes[0,0].set_xlabel('time_of_day', fontsize=12); axes[0,0].set_ylabel(f'Rata-rata Penyewaan ({selected_user_type})', fontsize=12)
            plt.setp(axes[0,0].get_xticklabels(), rotation=20, ha="right", rotation_mode="anchor")
            axes[0,0].grid(True, axis='y', linestyle='--', alpha=0.7)

            if selected_user_type == "Semua":
                time_of_day_melted_adv = time_of_day_analysis_df[['avg_casual_users', 'avg_registered_users']].reset_index().melt(id_vars='time_of_day', var_name='user_type', value_name='avg_users')
                time_of_day_melted_adv['user_type'] = time_of_day_melted_adv['user_type'].map({'avg_casual_users':'Casual', 'avg_registered_users':'Registered'})
                if not time_of_day_melted_adv.empty:
                    sns.barplot(x='time_of_day', y='avg_users', hue='user_type', data=time_of_day_melted_adv, ax=axes[0,1], palette={'Casual': 'lightcoral', 'Registered': 'steelblue'}, order=[t for t in TIME_OF_DAY_ORDER if t in time_of_day_melted_adv['time_of_day'].values])
                    axes[0,1].legend(title="Tipe Pengguna")
                else: axes[0,1].text(0.5, 0.5, 'Data pengguna tidak cukup', ha='center', va='center', transform=axes[0,1].transAxes)
            else:
                axes[0,1].text(0.5, 0.5, f'Menampilkan data untuk\n{selected_user_type}', ha='center', va='center', transform=axes[0,1].transAxes, fontsize=12)
            axes[0,1].set_title('Rata-rata Pengguna Casual vs Registered per Segmen Waktu', fontsize=14); axes[0,1].set_xlabel('time_of_day', fontsize=12); axes[0,1].set_ylabel('Rata-rata Penyewaan (Semua)', fontsize=12)
            plt.setp(axes[0,1].get_xticklabels(), rotation=20, ha="right", rotation_mode="anchor")
            axes[0,1].grid(True, axis='y', linestyle='--', alpha=0.7)

            sns.barplot(x=time_of_day_analysis_df.index, y='avg_temp_actual', data=time_of_day_analysis_df, ax=axes[1,0], palette='Oranges_r', order=[t for t in TIME_OF_DAY_ORDER if t in time_of_day_analysis_df.index])
            axes[1,0].set_title('Rata-rata Suhu Aktual (°C) per Segmen Waktu', fontsize=14); axes[1,0].set_xlabel('time_of_day', fontsize=12); axes[1,0].set_ylabel('Rata-rata Suhu (°C)', fontsize=12)
            plt.setp(axes[1,0].get_xticklabels(), rotation=20, ha="right", rotation_mode="anchor")
            axes[1,0].grid(True, axis='y', linestyle='--', alpha=0.7)

            weather_counts_by_time = adv_analysis_df.groupby(['time_of_day', 'weather_condition']).size().unstack(fill_value=0)
            if not weather_counts_by_time.empty:
                ordered_weather_cols_adv = [w for w in WEATHER_ORDER if w in weather_counts_by_time.columns]
                weather_counts_by_time = weather_counts_by_time.reindex(columns=ordered_weather_cols_adv, fill_value=0)
                weather_proportions_by_time = weather_counts_by_time.apply(lambda x: x / x.sum() * 100 if x.sum() > 0 else x, axis=1).reindex(TIME_OF_DAY_ORDER).dropna(how='all')
                if not weather_proportions_by_time.empty and not weather_proportions_by_time.isnull().all().all():
                    weather_proportions_by_time.plot(kind='bar', stacked=True, ax=axes[1,1], colormap='Spectral', width=0.8)
                    axes[1,1].set_title('Proporsi Kondisi Cuaca (%) per Segmen Waktu', fontsize=14); axes[1,1].set_xlabel('time_of_day', fontsize=12); axes[1,1].set_ylabel('Persentase (%)', fontsize=12)
                    plt.setp(axes[1,1].get_xticklabels(), rotation=20, ha="right", rotation_mode="anchor")
                    axes[1,1].legend(title='Kondisi Cuaca', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small'); axes[1,1].grid(True, axis='y', linestyle='--', alpha=0.7)
                else: axes[1,1].text(0.5, 0.5, 'Tidak ada data proporsi cuaca', ha='center', va='center', transform=axes[1,1].transAxes)
            else: axes[1,1].text(0.5, 0.5, 'Tidak ada data proporsi cuaca (pivot)', ha='center', va='center', transform=axes[1,1].transAxes)
            plt.tight_layout(rect=[0, 0, 1, 0.97]); st.pyplot(fig_adv)
        else:
            st.info("Tidak ada data yang cukup untuk analisis lanjutan berdasarkan segmen waktu dengan filter saat ini.")
    else:
        st.warning("Tidak ada data atau kolom yang dibutuhkan untuk Analisis Lanjutan berdasarkan filter Anda.")

# --- Kesimpulan dan Rekomendasi ---
st.sidebar.markdown("---")
st.sidebar.info("Dashboard ini dibuat berdasarkan analisis dari Proyek Akhir Analisis Data Dicoding.")
st.sidebar.markdown("Nama: Muhammad Husain Fadhlillah") # Ganti dengan nama Anda

st.header("📌 Kesimpulan Utama & Rekomendasi Bisnis")
with st.expander("Lihat Detail Kesimpulan dan Rekomendasi Strategis"):
    st.markdown("""
    ### **Jawaban Pertanyaan Bisnis 1: Pola Penggunaan Sepeda**
    Pola penggunaan sepeda sangat dipengaruhi oleh faktor waktu dan kondisi cuaca:
    1.  **Pola Jam Harian:** Puncak pukul **08:00 pagi** dan **17:00-18:00 sore**.
    2.  **Pola Harian (Mingguan):** Lebih tinggi pada **hari kerja (Kamis & Jumat)**.
    3.  **Pola Bulanan & Musiman:** Puncak pada **Juni-September (Musim Gugur & Panas)**.
    4.  **Pengaruh Kondisi Cuaca:** Tertinggi saat **Cerah/Sedikit Berawan**, menurun signifikan saat hujan/salju.
    ### **Jawaban Pertanyaan Bisnis 2: Perbedaan Karakteristik Pengguna Casual vs Registered**
    1.  **Dominasi Pengguna Registered:** Sekitar **~81.2%** total penyewaan.
    2.  **Pola Penggunaan Berbeda:** **Registered** (komuting hari kerja), **Casual** (rekreasi akhir pekan & musim hangat).
    ### **Analisis Lanjutan (Segmentasi Waktu Penggunaan):**
    * **Pagi (05-10) & Sore (16-20):** Aktivitas tertinggi, didominasi *registered*.
    * **Siang (11-15):** Peningkatan kontribusi *casual*, suhu rata-rata tertinggi.
    * **Malam (21-04):** Aktivitas terendah.
    ---
    ### **💡 Rekomendasi Bisnis Strategis**
    1.  **Optimalisasi Operasional:** Fokus ketersediaan sepeda pada jam sibuk komuter (Registered) dan area rekreasi akhir pekan (Casual).
    2.  **Program Loyalitas & Akuisisi:** Konversi Casual ke Registered, program loyalitas untuk Registered.
    3.  **Inisiatif Musiman & Adaptasi Cuaca:** Promosi musim ramai, diskon musim sepi, mitigasi cuaca buruk.
    4.  **Penempatan & Alokasi Armada Cerdas:** Gunakan data heatmap untuk optimasi distribusi.
    """)

with st.expander("Tampilkan Data Tabel yang Telah Difilter"):
    st.markdown("#### Data Per Jam (Filtered)")
    if not hour_data_filtered.empty:
        st.dataframe(hour_data_filtered[['dteday', 'season_name', 'year', 'month_name', 'hr', 'weekday_name', 'weather_condition', 'temp_actual', 'hum_actual', 'casual', 'registered', 'cnt_display']].head())
        st.caption(f"Menampilkan {len(hour_data_filtered)} baris data per jam yang telah difilter.")
    else: st.info("Tidak ada data per jam untuk ditampilkan berdasarkan filter yang dipilih.")

    st.markdown("#### Data Harian (Filtered)")
    if not day_data_filtered.empty:
        st.dataframe(day_data_filtered[['dteday', 'season_name', 'year', 'month_name', 'weekday_name', 'weather_condition', 'temp_actual', 'hum_actual', 'casual', 'registered', 'cnt_display']].head())
        st.caption(f"Menampilkan {len(day_data_filtered)} baris data harian yang telah difilter.")
    else: st.info("Tidak ada data harian untuk ditampilkan berdasarkan filter yang dipilih.")