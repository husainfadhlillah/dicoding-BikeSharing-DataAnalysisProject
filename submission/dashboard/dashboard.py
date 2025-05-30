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
        color: #2c3e50;
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

# Sidebar untuk filter interaktif
st.sidebar.header("⚙️ Filter Data")

# Filter tanggal
st.sidebar.markdown("**Rentang Tanggal**")
if not day_df.empty:
    min_date_val = day_df['dteday'].min()
    max_date_val = day_df['dteday'].max()
    date_range = st.sidebar.date_input(
        "Pilih periode",
        value=[min_date_val, max_date_val],
        min_value=min_date_val,
        max_value=max_date_val
    )
else:
    st.sidebar.error("Data harian kosong, filter tanggal tidak dapat dimuat.")
    date_range = [pd.Timestamp('2011-01-01'), pd.Timestamp('2012-12-31')]


# Filter lainnya
st.sidebar.markdown("**Filter Tambahan**")
unique_years = hour_df['year'].unique() if not hour_df.empty else []
selected_year = st.sidebar.multiselect(
    "Tahun",
    options=unique_years,
    default=unique_years
)

unique_seasons = hour_df['season_name'].unique() if not hour_df.empty else []
selected_season = st.sidebar.multiselect(
    "Musim",
    options=unique_seasons,
    default=unique_seasons
)

unique_weather = hour_df['weather_condition'].unique() if not hour_df.empty else []
selected_weather = st.sidebar.multiselect(
    "Kondisi Cuaca",
    options=unique_weather,
    default=unique_weather
)

selected_user_type = st.sidebar.radio(
    "Jenis Pengguna",
    options=['Semua', 'Casual', 'Registered'],
    index=0
)

# Membuat salinan data untuk filter
hour_data_filtered = hour_df.copy()
day_data_filtered = day_df.copy()

# Filter data berdasarkan pilihan
if not hour_data_filtered.empty and len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
    
    hour_data_filtered = hour_data_filtered[
        (hour_data_filtered['dteday'] >= start_date) & 
        (hour_data_filtered['dteday'] <= end_date)
    ]
    day_data_filtered = day_data_filtered[
        (day_data_filtered['dteday'] >= start_date) & 
        (day_data_filtered['dteday'] <= end_date)
    ]

if selected_year and not hour_data_filtered.empty:
    hour_data_filtered = hour_data_filtered[hour_data_filtered['year'].isin(selected_year)]
    day_data_filtered = day_data_filtered[day_data_filtered['year'].isin(selected_year)]

if selected_season and not hour_data_filtered.empty:
    hour_data_filtered = hour_data_filtered[hour_data_filtered['season_name'].isin(selected_season)]
    day_data_filtered = day_data_filtered[day_data_filtered['season_name'].isin(selected_season)]

if selected_weather and not hour_data_filtered.empty:
    hour_data_filtered = hour_data_filtered[hour_data_filtered['weather_condition'].isin(selected_weather)]
    day_data_filtered = day_data_filtered[day_data_filtered['weather_condition'].isin(selected_weather)]

# Filter berdasarkan jenis pengguna
if not hour_data_filtered.empty:
    if selected_user_type == 'Casual':
        hour_data_filtered['cnt_display'] = hour_data_filtered['casual']
        if not day_data_filtered.empty:
            day_data_filtered['cnt_display'] = day_data_filtered['casual']
    elif selected_user_type == 'Registered':
        hour_data_filtered['cnt_display'] = hour_data_filtered['registered']
        if not day_data_filtered.empty:
            day_data_filtered['cnt_display'] = day_data_filtered['registered']
    else: # Semua
        hour_data_filtered['cnt_display'] = hour_data_filtered['cnt']
        if not day_data_filtered.empty:
            day_data_filtered['cnt_display'] = day_data_filtered['cnt']
else:
    if not day_data_filtered.empty : # Jika hour_data_filtered kosong tapi day_data_filtered tidak
        if selected_user_type == 'Casual':
            day_data_filtered['cnt_display'] = day_data_filtered['casual']
        elif selected_user_type == 'Registered':
            day_data_filtered['cnt_display'] = day_data_filtered['registered']
        else:
            day_data_filtered['cnt_display'] = day_data_filtered['cnt']

# Judul dashboard
st.title("📊 Dashboard Analisis Penyewaan Sepeda")
st.markdown("""
    Visualisasi interaktif pola penggunaan sepeda berdasarkan waktu, cuaca, dan jenis pengguna.
""")

# Tab untuk organisasi konten
tab1, tab2, tab3, tab4 = st.tabs(["📈 Analisis Waktu", "🌤️ Analisis Cuaca", "👥 Analisis Pengguna", "🔬 Analisis Lanjutan"])

with tab1:
    st.header("🕒 Analisis Berdasarkan Waktu")
    
    if not hour_data_filtered.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Rata-rata Penyewaan Sepeda per Jam")
            hourly_pattern = hour_data_filtered.groupby('hr')['cnt_display'].mean().reset_index()
            fig1, ax = plt.subplots(figsize=(10, 5))
            sns.lineplot(x='hr', y='cnt_display', data=hourly_pattern, marker='o', linewidth=2, ax=ax, color='dodgerblue')
            ax.set_title('Rata-rata Penyewaan per Jam', fontsize=15)
            ax.set_xlabel('Jam', fontsize=12)
            ax.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
            ax.set_xticks(range(0, 24))
            ax.grid(True, alpha=0.3)
            st.pyplot(fig1)

            st.subheader("Rata-rata Penyewaan Sepeda per Bulan")
            monthly_pattern = hour_data_filtered.groupby('month_name')['cnt_display'].mean().reindex(calendar.month_name[1:]).reset_index()
            fig_month, ax_month = plt.subplots(figsize=(10, 5))
            sns.lineplot(x='month_name', y='cnt_display', data=monthly_pattern, marker='o', linewidth=2, color='green', sort=False, ax=ax_month)
            ax_month.set_title('Rata-rata Penyewaan per Bulan', fontsize=15)
            ax_month.set_xlabel('Bulan', fontsize=12)
            ax_month.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
            ax_month.tick_params(axis='x', rotation=45)
            ax_month.grid(True, alpha=0.3)
            st.pyplot(fig_month)

        with col2:
            st.subheader("Rata-rata Penyewaan Sepeda per Hari dalam Seminggu")
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            daily_pattern_weekday = hour_data_filtered.groupby('weekday_name')['cnt_display'].mean().reindex(weekday_order).reset_index()
            fig_day, ax_day = plt.subplots(figsize=(10, 5))
            sns.barplot(x='weekday_name', y='cnt_display', data=daily_pattern_weekday, palette='viridis', ax=ax_day)
            ax_day.set_title('Rata-rata Penyewaan per Hari', fontsize=15)
            ax_day.set_xlabel('Hari', fontsize=12)
            ax_day.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
            ax_day.grid(True, axis='y', alpha=0.3)
            st.pyplot(fig_day)

            st.subheader("Rata-rata Penyewaan Sepeda per Musim")
            season_order = ['Spring', 'Summer', 'Fall', 'Winter']
            seasonal_pattern = hour_data_filtered.groupby('season_name')['cnt_display'].mean().reindex(season_order).reset_index()
            fig_season, ax_season = plt.subplots(figsize=(10, 5))
            sns.barplot(x='season_name', y='cnt_display', data=seasonal_pattern, palette='magma', ax=ax_season)
            ax_season.set_title('Rata-rata Penyewaan per Musim', fontsize=15)
            ax_season.set_xlabel('Musim', fontsize=12)
            ax_season.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
            ax_season.grid(True, axis='y', alpha=0.3)
            st.pyplot(fig_season)
            
        st.subheader("Heatmap Penyewaan: Jam vs Hari")
        hour_weekday_heatmap = hour_data_filtered.pivot_table(
            index='hr', 
            columns='weekday_name', 
            values='cnt_display', 
            aggfunc='mean'
        )
        if not hour_weekday_heatmap.empty:
            hour_weekday_heatmap = hour_weekday_heatmap.reindex(
                columns=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            )
            fig_hm_day, ax_hm_day = plt.subplots(figsize=(12, 8))
            sns.heatmap(hour_weekday_heatmap, cmap='viridis', annot=False, fmt='.0f', 
                       cbar_kws={'label': 'Rata-rata Penyewaan'}, ax=ax_hm_day)
            ax_hm_day.set_title('Heatmap Penyewaan: Jam vs Hari', fontsize=16)
            ax_hm_day.set_xlabel('Hari', fontsize=12)
            ax_hm_day.set_ylabel('Jam', fontsize=12)
            st.pyplot(fig_hm_day)

        st.subheader("Heatmap Penyewaan: Jam vs Bulan")
        month_order_heatmap = calendar.month_name[1:]
        hour_month_heatmap = hour_data_filtered.pivot_table(index='hr', columns='month_name', values='cnt_display', aggfunc='mean')
        if not hour_month_heatmap.empty:
            hour_month_heatmap = hour_month_heatmap.reindex(columns=month_order_heatmap)
            fig_hm_month, ax_hm_month = plt.subplots(figsize=(14, 8))
            sns.heatmap(hour_month_heatmap, cmap='YlGnBu', annot=False, fmt=".0f", linewidths=.5, cbar_kws={'label': 'Rata-rata Penyewaan'}, ax=ax_hm_month)
            ax_hm_month.set_title('Heatmap Rata-rata Penyewaan Sepeda: Jam vs Bulan', fontsize=16)
            ax_hm_month.set_xlabel('Bulan', fontsize=14)
            ax_hm_month.set_ylabel('Jam dalam Sehari', fontsize=14)
            ax_hm_month.tick_params(axis='x', rotation=45, ha='right')
            st.pyplot(fig_hm_month)
    else:
        st.warning("Tidak ada data untuk ditampilkan berdasarkan filter yang dipilih.")


with tab2:
    st.header("🌤️ Analisis Berdasarkan Cuaca")
    
    if not hour_data_filtered.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Rata-rata Penyewaan berdasarkan Kondisi Cuaca")
            weather_impact = hour_data_filtered.groupby('weather_condition')['cnt_display'].mean().reset_index()
            weather_order = ['Clear/Few clouds', 'Mist/Cloudy', 'Light Snow/Rain', 'Heavy Rain/Snow/Fog']
            weather_impact['weather_condition'] = pd.Categorical(weather_impact['weather_condition'], categories=weather_order, ordered=True)
            weather_impact = weather_impact.sort_values('weather_condition')

            fig3, ax = plt.subplots(figsize=(10, 5))
            sns.barplot(x='weather_condition', y='cnt_display', data=weather_impact, palette='viridis', ax=ax)
            ax.set_title('Rata-rata Penyewaan berdasarkan Kondisi Cuaca', fontsize=15)
            ax.set_xlabel('Kondisi Cuaca', fontsize=12)
            ax.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
            ax.tick_params(axis='x', rotation=15, ha='right')
            ax.grid(True, axis='y', alpha=0.3)
            st.pyplot(fig3)
            
        with col2:
            st.subheader("Heatmap Penyewaan: Jam vs Kondisi Cuaca")
            hour_weather_heatmap = hour_data_filtered.pivot_table(index='hr', columns='weather_condition', values='cnt_display', aggfunc='mean')
            if not hour_weather_heatmap.empty:
                hour_weather_heatmap = hour_weather_heatmap.reindex(columns=weather_order, fill_value=0) # fill_value for missing weather conditions for some hours
                fig_hm_weather, ax_hm_weather = plt.subplots(figsize=(10, 8))
                sns.heatmap(hour_weather_heatmap, cmap='magma_r', annot=True, fmt=".0f", linewidths=.5, cbar_kws={'label': 'Rata-rata Penyewaan'}, ax=ax_hm_weather)
                ax_hm_weather.set_title('Heatmap Penyewaan: Jam vs Kondisi Cuaca', fontsize=16)
                ax_hm_weather.set_xlabel('Kondisi Cuaca', fontsize=12)
                ax_hm_weather.set_ylabel('Jam', fontsize=12)
                ax_hm_weather.tick_params(axis='x', rotation=15, ha='right')
                st.pyplot(fig_hm_weather)
    else:
        st.warning("Tidak ada data untuk ditampilkan berdasarkan filter yang dipilih.")


with tab3:
    st.header("👥 Analisis Berdasarkan Pengguna")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Proporsi Pengguna Casual vs Registered")
        if not day_data_filtered.empty:
            total_users_pie = day_data_filtered[['casual', 'registered']].sum()
            if total_users_pie.sum() > 0 : # Hanya tampilkan pie chart jika ada data
                labels = ['Casual', 'Registered']
                fig5, ax = plt.subplots(figsize=(8, 5))
                ax.pie(total_users_pie, labels=labels, autopct='%1.1f%%', startangle=90, 
                       colors=['#ff9999', '#66b3ff'])
                ax.set_title('Proporsi Pengguna Casual vs Registered', fontsize=15)
                ax.axis('equal')
                st.pyplot(fig5)
            else:
                st.info("Tidak ada data penyewaan untuk jenis pengguna ini dengan filter yang dipilih.")
        else:
             st.warning("Tidak ada data harian untuk ditampilkan berdasarkan filter yang dipilih.")

    with col2:
        st.subheader("Penggunaan per Hari Kerja vs Akhir Pekan/Libur")
        if not hour_data_filtered.empty and selected_user_type == "Semua": # Grafik ini lebih bermakna untuk semua pengguna
            workday_agg_df = hour_data_filtered.groupby('workingday').agg(
                avg_casual=('casual', 'mean'),
                avg_registered=('registered', 'mean')
            ).reset_index()
            workday_agg_df['workingday'] = workday_agg_df['workingday'].map({0: 'Akhir Pekan/Libur', 1: 'Hari Kerja'})
            workday_melted = workday_agg_df.melt(id_vars='workingday', value_vars=['avg_casual', 'avg_registered'], var_name='tipe_pengguna', value_name='rata_penyewaan')
            
            fig_workday, ax_workday = plt.subplots(figsize=(8, 5))
            sns.barplot(x='workingday', y='rata_penyewaan', hue='tipe_pengguna', data=workday_melted, palette={'avg_casual': 'skyblue', 'avg_registered': 'darkblue'}, ax=ax_workday)
            ax_workday.set_title('Rata-rata Penyewaan per Tipe Pengguna', fontsize=15)
            ax_workday.set_xlabel('Status Hari', fontsize=12)
            ax_workday.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
            st.pyplot(fig_workday)
        elif selected_user_type != "Semua":
            st.info(f"Grafik perbandingan pengguna di hari kerja vs akhir pekan/libur hanya ditampilkan untuk tipe pengguna 'Semua'.")
        else:
            st.warning("Tidak ada data untuk ditampilkan berdasarkan filter yang dipilih.")

    if not hour_data_filtered.empty and selected_user_type == "Semua":
        st.subheader("Pola Penggunaan per Jam (Casual vs Registered)")
        user_type_hourly_df = hour_data_filtered.groupby('hr').agg(
            avg_casual=('casual', 'mean'),
            avg_registered=('registered', 'mean')
        ).reset_index()
        fig_user_hr, ax_user_hr = plt.subplots(figsize=(12,6))
        ax_user_hr.plot(user_type_hourly_df['hr'], user_type_hourly_df['avg_casual'], label='Casual', marker='o', color='skyblue')
        ax_user_hr.plot(user_type_hourly_df['hr'], user_type_hourly_df['avg_registered'], label='Registered', marker='x', color='darkblue')
        ax_user_hr.set_title('Rata-rata Penyewaan per Jam berdasarkan Tipe Pengguna', fontsize=15)
        ax_user_hr.set_xlabel('Jam', fontsize=12)
        ax_user_hr.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
        ax_user_hr.set_xticks(range(0,24))
        ax_user_hr.legend()
        ax_user_hr.grid(True, alpha=0.3)
        st.pyplot(fig_user_hr)

        st.subheader("Pola Penggunaan per Musim (Casual vs Registered)")
        season_order_user = ['Spring', 'Summer', 'Fall', 'Winter']
        user_type_season_df = hour_data_filtered.groupby('season_name').agg(
            avg_casual=('casual', 'mean'),
            avg_registered=('registered', 'mean')
        ).reset_index()
        user_type_season_df['season_name'] = pd.Categorical(user_type_season_df['season_name'], categories=season_order_user, ordered=True)
        user_type_season_df = user_type_season_df.sort_values('season_name')
        user_type_season_melted = user_type_season_df.melt(id_vars='season_name', value_vars=['avg_casual', 'avg_registered'], var_name='tipe_pengguna', value_name='rata_penyewaan')

        fig_user_season, ax_user_season = plt.subplots(figsize=(10,5))
        sns.barplot(x='season_name', y='rata_penyewaan', hue='tipe_pengguna', data=user_type_season_melted, palette={'avg_casual': 'skyblue', 'avg_registered': 'darkblue'}, ax=ax_user_season)
        ax_user_season.set_title('Rata-rata Penyewaan per Musim berdasarkan Tipe Pengguna', fontsize=15)
        ax_user_season.set_xlabel('Musim', fontsize=12)
        ax_user_season.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
        st.pyplot(fig_user_season)
    elif selected_user_type != "Semua":
        st.info(f"Grafik perbandingan pengguna per jam & musim hanya ditampilkan untuk tipe pengguna 'Semua'.")

with tab4:
    st.header("🔬 Analisis Lanjutan: Segmentasi Pengguna Berdasarkan Waktu")
    
    if not hour_data_filtered.empty:
        # Fungsi untuk Manual Grouping berdasarkan waktu
        def assign_time_of_day(hr):
            if 5 <= hr <= 10:
                return 'Pagi (05-10)'
            elif 11 <= hr <= 15:
                return 'Siang (11-15)'
            elif 16 <= hr <= 20:
                return 'Sore (16-20)'
            else: 
                return 'Malam (21-04)'

        hour_data_filtered['time_of_day'] = hour_data_filtered['hr'].apply(assign_time_of_day)
        time_of_day_order = ['Pagi (05-10)', 'Siang (11-15)', 'Sore (16-20)', 'Malam (21-04)']
        
        time_of_day_analysis = hour_data_filtered.groupby('time_of_day').agg(
            avg_total_users=('cnt_display', 'mean'),
            avg_casual_users=('casual', 'mean'),
            avg_registered_users=('registered', 'mean'),
            avg_temp=('temp_actual', 'mean'),
            avg_humidity=('hum_actual', 'mean'),
        ).reindex(time_of_day_order)

        fig_adv, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig_adv.suptitle('Analisis Pengguna Berdasarkan Segmen Waktu (Manual Grouping)', fontsize=16)

        sns.barplot(x=time_of_day_analysis.index, y='avg_total_users', data=time_of_day_analysis, ax=axes[0,0], palette='Blues_r', order=time_of_day_order)
        axes[0,0].set_title('Rata-rata Total Penyewaan')
        axes[0,0].set_ylabel('Rata-rata Jumlah Penyewaan')
        axes[0,0].tick_params(axis='x', rotation=15, ha='right')

        time_of_day_melted = time_of_day_analysis[['avg_casual_users', 'avg_registered_users']].reset_index().melt(id_vars='time_of_day', var_name='user_type', value_name='avg_users')
        time_of_day_melted['time_of_day'] = pd.Categorical(time_of_day_melted['time_of_day'], categories=time_of_day_order, ordered=True)
        sns.barplot(x='time_of_day', y='avg_users', hue='user_type', data=time_of_day_melted, ax=axes[0,1], palette={'avg_casual_users': 'skyblue', 'avg_registered_users': 'darkblue'}, order=time_of_day_order)
        axes[0,1].set_title('Rata-rata Casual vs Registered')
        axes[0,1].set_ylabel('Rata-rata Jumlah Penyewaan')
        axes[0,1].tick_params(axis='x', rotation=15, ha='right')

        sns.barplot(x=time_of_day_analysis.index, y='avg_temp', data=time_of_day_analysis, ax=axes[1,0], palette='Oranges_r', order=time_of_day_order)
        axes[1,0].set_title('Rata-rata Suhu (°C)')
        axes[1,0].set_ylabel('Rata-rata Suhu (°C)')
        axes[1,0].tick_params(axis='x', rotation=15, ha='right')
        
        weather_counts_by_time = hour_data_filtered.groupby(['time_of_day', 'weather_condition']).size().unstack(fill_value=0)
        weather_proportions_by_time = weather_counts_by_time.apply(lambda x: x / x.sum() * 100, axis=1).reindex(time_of_day_order)
        weather_proportions_by_time.plot(kind='bar', stacked=True, ax=axes[1,1], colormap='Spectral')
        axes[1,1].set_title('Proporsi Kondisi Cuaca')
        axes[1,1].set_ylabel('Persentase (%)')
        axes[1,1].tick_params(axis='x', rotation=15, ha='right')
        axes[1,1].legend(title='Kondisi Cuaca', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        st.pyplot(fig_adv)
    else:
        st.warning("Tidak ada data untuk ditampilkan berdasarkan filter yang dipilih.")

# Kesimpulan dan rekomendasi dari notebook
st.header("📌 Kesimpulan dan Rekomendasi")
with st.expander("Lihat Detail Kesimpulan dan Rekomendasi"):
    st.markdown("""
    ### **Pertanyaan 1: Pola Penggunaan Sepeda Berdasarkan Faktor Waktu (Jam, Hari, Bulan, Musim) dan Faktor Cuaca**

    Pola penggunaan sepeda menunjukkan variasi yang signifikan berdasarkan faktor waktu dan kondisi cuaca:

    1.  **Pola Berdasarkan Jam (Hourly Pattern):**
        * Terdapat pola **bimodal** yang jelas dalam penggunaan sepeda harian, terutama pada hari kerja.
        * **Puncak Pagi:** Terjadi sekitar pukul 08:00 pagi, dengan rata-rata penyewaan yang tinggi (sekitar 350-360 penyewaan), didominasi oleh pengguna *registered* yang kemungkinan besar adalah komuter.
        * **Puncak Sore:** Terjadi sekitar pukul 17:00-18:00 sore, dan ini merupakan puncak tertinggi dalam sehari (sekitar 450-470 penyewaan), juga didominasi oleh pengguna *registered*.
        * **Penggunaan Siang Hari (di luar puncak):** Relatif stabil antara pukul 10:00 hingga 15:00 (sekitar 175-260 penyewaan).
        * **Penggunaan Terendah:** Terjadi pada dini hari, sekitar pukul 03:00-04:00 pagi (kurang dari 10 penyewaan).
        * Heatmap jam vs. hari menunjukkan pola komuter ini sangat kuat pada hari Senin-Jumat, sedangkan pada Sabtu-Minggu aktivitas lebih tinggi dan merata pada siang hingga sore hari.

    2.  **Pola Berdasarkan Hari dalam Seminggu (Daily Pattern):**
        * Rata-rata penyewaan cenderung lebih tinggi pada **hari kerja (Kamis dan Jumat tertinggi)** dibandingkan awal pekan (Senin).
        * **Akhir pekan (Sabtu dan Minggu)** juga menunjukkan tingkat penyewaan yang cukup tinggi, mengindikasikan penggunaan untuk tujuan rekreasi, dengan aktivitas yang lebih merata dari siang hingga sore.

    3.  **Pola Berdasarkan Bulan dan Musim (Monthly & Seasonal Pattern):**
        * Penggunaan sepeda menunjukkan tren musiman yang jelas.
        * **Puncak Penggunaan:** Terjadi pada bulan-bulan hangat, yaitu dari **Juni hingga September (Musim Panas dan Gugur)**. Musim **Gugur (Fall)** mencatatkan rata-rata penyewaan tertinggi (sekitar 236 penyewaan/jam), diikuti Musim Panas (Summer, sekitar 208 penyewaan/jam).
        * **Penggunaan Terendah:** Terjadi pada bulan-bulan dingin, yaitu **Januari dan Februari (Musim Semi/Spring berdasarkan mapping dataset)**, di mana Musim Semi mencatatkan rata-rata terendah (sekitar 111 penyewaan/jam). Musim Dingin (Winter) masih lebih tinggi dari Musim Semi.
        * Heatmap jam vs. bulan dan jam vs. musim mengkonfirmasi bahwa puncak penggunaan pagi dan sore lebih intens pada bulan-bulan hangat/musim panas dan gugur.

    4.  **Pengaruh Kondisi Cuaca (Weather Influence):**
        * Kondisi cuaca sangat memengaruhi jumlah penyewaan.
        * **Cuaca Ideal ("Clear/Few clouds"):** Menghasilkan rata-rata penyewaan tertinggi (sekitar 205 penyewaan/jam).
        * **Cuaca Berkabut/Berawan ("Mist/Cloudy"):** Masih menunjukkan tingkat penyewaan yang cukup tinggi (sekitar 175 penyewaan/jam).
        * **Cuaca Hujan Ringan/Salju Ringan ("Light Snow/Rain"):** Menyebabkan penurunan signifikan (sekitar 112 penyewaan/jam).
        * **Cuaca Buruk ("Heavy Rain/Snow/Fog"):** Memiliki dampak negatif paling besar, menurunkan penyewaan secara drastis (sekitar 74 penyewaan/jam, meskipun data untuk kategori ini terbatas).

    ### **Pertanyaan 2: Apa Perbedaan Karakteristik Antara Pengguna Casual dan Registered, dan Bagaimana Ini Dapat Memengaruhi Strategi Bisnis?**

    Terdapat perbedaan karakteristik dan perilaku yang jelas antara pengguna *casual* dan *registered*:

    1.  **Dominasi Pengguna Registered:**
        * Pengguna **registered** mendominasi secara signifikan, mencakup **81,2%** dari total penyewaan sepeda. Ini menunjukkan adanya basis pelanggan loyal yang kuat dan menjadi tulang punggung operasional.
        * Pengguna **casual** hanya menyumbang **18,8%** dari total penyewaan.

    2.  **Pola Penggunaan Berdasarkan Waktu:**
        * **Pengguna Registered:**
            * Menunjukkan pola penggunaan yang sangat kuat terkait **komuting** pada hari kerja, dengan puncak aktivitas pada pukul 08:00 pagi dan 17:00-18:00 sore.
            * Proporsi mereka paling tinggi pada jam-jam sibuk pagi dan sore di hari kerja.
        * **Pengguna Casual:**
            * Lebih aktif pada **akhir pekan dan hari libur**, dengan puncak penggunaan di siang hingga sore hari (sekitar pukul 11:00-16:00).
            * Pada hari kerja, penggunaan casual cenderung lebih tinggi pada jam-jam di luar puncak komuter, yaitu siang hari.
            * Analisis manual grouping berdasarkan segmen waktu (Pagi, Siang, Sore, Malam) mengkonfirmasi bahwa pengguna casual lebih banyak di segmen Siang dan Sore, sementara Registered sangat dominan di Pagi dan Sore (terutama jam komuter).

    3.  **Pola Penggunaan Berdasarkan Musim dan Cuaca:**
        * **Pengguna Casual:** Menunjukkan proporsi penggunaan yang lebih tinggi selama musim-musim dengan cuaca hangat seperti **Musim Panas (Summer) dan Gugur (Fall)** dibandingkan pengguna *registered*.
        * Sensitivitas terhadap cuaca buruk tampak lebih tinggi pada pengguna *casual*.

    4.  **Implikasi Strategis:**
        * **Pengguna Registered:** Merupakan target utama untuk program retensi dan peningkatan frekuensi penggunaan karena kontribusi mereka yang besar dan stabil.
        * **Pengguna Casual:** Mewakili potensi pertumbuhan yang signifikan. Strategi untuk mengkonversi pengguna *casual* menjadi *registered* dapat meningkatkan loyalitas dan pendapatan (misalnya, penawaran khusus untuk registrasi setelah beberapa kali sewa casual, atau paket akhir pekan untuk registrasi). Penargetan promosi untuk aktivitas rekreasi pada akhir pekan atau selama musim hangat bisa efektif untuk segmen ini.

    ### **Kesimpulan Umum dari Analisis Lanjutan (Manual Grouping):**
    Pengelompokan waktu penggunaan menjadi Pagi (05-10), Siang (11-15), Sore (16-20), dan Malam (21-04) memperjelas bahwa:
    * Segmen **Pagi** dan **Sore** memiliki rata-rata total penyewaan tertinggi, dengan dominasi kuat pengguna *registered*. Rata-rata suhu di segmen ini moderat.
    * Segmen **Siang** menunjukkan peningkatan kontribusi pengguna *casual* dan memiliki suhu rata-rata tertinggi.
    * Segmen **Malam** memiliki aktivitas terendah untuk semua jenis pengguna dengan suhu rata-rata yang lebih rendah.
    * Kondisi cuaca dominan ("Clear/Few clouds") relatif serupa di semua segmen waktu, menunjukkan bahwa pola aktivitas harian lebih berpengaruh pada variasi penggunaan antar segmen waktu dibandingkan variasi cuaca signifikan dalam sehari.
    
    ### **Rekomendasi Bisnis**
    1.  **Optimalisasi Operasional & Penargetan Pengguna:**
        * **Jam Sibuk Komuter (Registered Users):**
            * Pastikan ketersediaan sepeda yang cukup di area perkantoran/bisnis dan stasiun transportasi publik pada jam 07:00-09:00 dan 16:00-19:00 pada hari kerja (Senin-Jumat).
            * Tawarkan \"Paket Komuter Mingguan/Bulanan\" untuk pengguna *registered* dengan tarif diskon atau bonus poin loyalitas untuk penggunaan rutin di jam sibuk.
        * **Akhir Pekan & Hari Libur (Casual Users):**
            * Tingkatkan ketersediaan sepeda di area rekreasi, taman, dan pusat wisata pada hari Sabtu dan Minggu, terutama pukul 11:00-16:00.
            * Buat promosi \"Weekend Pass\" atau \"Family Day Out Package\" untuk menarik lebih banyak pengguna *casual*.
            * Pertimbangkan untuk menawarkan sepeda jenis tandem atau dengan keranjang tambahan di lokasi wisata untuk pengguna *casual*.
        * **Penggunaan Siang Hari (Hari Kerja):**
            * Untuk meningkatkan utilisasi di luar jam puncak (10:00-15:00) pada hari kerja, tawarkan \"Diskon Makan Siang\" atau \"Happy Hour Ride\" dengan tarif lebih rendah.

    2.  **Program Loyalitas & Konversi Pengguna:**
        * **Konversi Casual ke Registered:**
            * Berikan insentif bagi pengguna *casual* untuk beralih ke *registered*, misalnya diskon pada registrasi pertama setelah beberapa kali penyewaan, atau akumulasi poin dari sewa *casual* yang bisa ditukarkan saat registrasi.
        * **Pengembangan Program Loyalitas Registered:**
            * Perkuat program loyalitas untuk pengguna *registered* dengan tingkatan keanggotaan (misalnya Silver, Gold, Platinum) berdasarkan frekuensi penggunaan, yang memberikan benefit tambahan seperti gratis sewa beberapa jam, prioritas ketersediaan, atau akses ke event eksklusif.

    3.  **Inisiatif Musiman & Berbasis Cuaca:**
        * **Promosi Musim Ramai (Gugur & Panas):**
            * Maksimalkan promosi selama musim gugur dan panas (Juni-September) saat penggunaan sepeda sedang tinggi.
            * Adakan event bersepeda tematik seperti \"Summer Night Ride\" atau \"Autumn Color Tour\".
        * **Strategi Musim Sepi (Semi & Dingin Awal):**
            * Tawarkan diskon khusus atau promosi \"Warm Ride\" (misalnya, gratis minuman hangat di kafe mitra) untuk mendorong penggunaan di musim semi atau awal musim dingin (Januari-Februari).
        * **Mitigasi Risiko Cuaca:**
            * Integrasikan prediksi cuaca *real-time* dalam aplikasi penyewaan.
            * Tawarkan \"Rain Guarantee\" berupa diskon untuk penyewaan berikutnya jika durasi sewa terpotong oleh hujan lebat, atau sediakan sepeda \"rain-ready\" (dengan fender/pelindung hujan) di beberapa titik strategis.

    4.  **Strategi Penempatan & Alokasi Armada:**
        * Gunakan data heatmap jam vs. hari, jam vs. bulan, dan jam vs. musim untuk optimasi penempatan armada sepeda. Pastikan konsentrasi sepeda lebih tinggi di area-area yang menunjukkan permintaan puncak pada waktu-waktu spesifik tersebut.
        * Analisis lebih lanjut proporsi pengguna *casual* vs *registered* per stasiun/lokasi dapat membantu penyesuaian jenis promosi yang lebih efektif di area tertentu.
    """)

# Tampilkan data yang difilter
with st.expander("📊 Lihat Data yang Difilter"):
    if not hour_data_filtered.empty:
        st.write(f"Menampilkan {len(hour_data_filtered)} baris data (per jam)")
        st.dataframe(hour_data_filtered.head())
    else:
        st.write("Tidak ada data untuk ditampilkan berdasarkan filter yang dipilih.")