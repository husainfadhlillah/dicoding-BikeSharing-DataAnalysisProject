# Import
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

# Custom CSS untuk gradient background
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #6a11cb, #2575fc);
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load data
@st.cache_data
def load_data():
    hour_data = pd.read_csv('main_data/hour_data_clean.csv')
    day_data = pd.read_csv('main_data/day_data_clean.csv')
    return hour_data, day_data

hour_data, day_data = load_data()

# Sidebar untuk filter data
st.sidebar.header("Filter Data")
selected_year = st.sidebar.selectbox("Pilih Tahun", ['All'] + list(hour_data['year'].unique()))
selected_season = st.sidebar.selectbox("Pilih Musim", ['All'] + list(hour_data['season_name'].unique()))

# Filter data berdasarkan pilihan
if selected_year != 'All':
    hour_data = hour_data[hour_data['year'] == selected_year]
    day_data = day_data[day_data['year'] == selected_year]

if selected_season != 'All':
    hour_data = hour_data[hour_data['season_name'] == selected_season]
    day_data = day_data[day_data['season_name'] == selected_season]

# Judul Dashboard
st.title("Bike Sharing Dashboard")
st.markdown("""
    Dashboard ini menampilkan analisis data Bike Sharing Dataset berdasarkan waktu, cuaca, dan jenis pengguna.
""")

# Visualisasi 1: Pola Penggunaan Sepeda berdasarkan Jam
st.header("Pola Penggunaan Sepeda berdasarkan Jam")
hourly_pattern = hour_data.groupby('hr')['cnt'].mean().reset_index()

fig1, ax1 = plt.subplots(figsize=(12, 6))
sns.lineplot(x='hr', y='cnt', data=hourly_pattern, marker='o', linewidth=2, ax=ax1)
ax1.set_title('Rata-rata Penyewaan Sepeda berdasarkan Jam', fontsize=15)
ax1.set_xlabel('Jam', fontsize=12)
ax1.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
ax1.set_xticks(range(0, 24))
ax1.grid(True, alpha=0.3)
st.pyplot(fig1)

# Visualisasi 2: Pengaruh Cuaca terhadap Penyewaan Sepeda
st.header("Pengaruh Cuaca terhadap Penyewaan Sepeda")
weather_impact = hour_data.groupby('weather_condition')['cnt'].mean().reset_index()

fig2, ax2 = plt.subplots(figsize=(12, 6))
sns.barplot(x='weather_condition', y='cnt', data=weather_impact, palette='viridis', ax=ax2)
ax2.set_title('Rata-rata Penyewaan Sepeda berdasarkan Kondisi Cuaca', fontsize=15)
ax2.set_xlabel('Kondisi Cuaca', fontsize=12)
ax2.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
ax2.grid(True, alpha=0.3)
st.pyplot(fig2)

# Visualisasi 3: Heatmap Jam vs Hari
st.header("Heatmap Penyewaan Sepeda: Jam vs Hari")
hour_weekday_heatmap = hour_data.pivot_table(index='hr', columns='weekday_name', values='cnt', aggfunc='mean')
hour_weekday_heatmap = hour_weekday_heatmap.reindex(columns=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

fig3, ax3 = plt.subplots(figsize=(16, 10))
sns.heatmap(hour_weekday_heatmap, cmap='viridis', annot=False, fmt='.0f', cbar_kws={'label': 'Rata-rata Penyewaan'}, ax=ax3)
ax3.set_title('Heatmap Penyewaan Sepeda: Jam vs Hari', fontsize=16)
ax3.set_xlabel('Hari', fontsize=12)
ax3.set_ylabel('Jam', fontsize=12)
st.pyplot(fig3)

# Visualisasi 4: Proporsi Pengguna Casual vs Registered
st.header("Proporsi Pengguna Casual vs Registered")
total_users = day_data[['casual', 'registered']].sum()
labels = ['Casual', 'Registered']

fig4, ax4 = plt.subplots(figsize=(10, 8))
ax4.pie(total_users, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#ff9999', '#66b3ff'])
ax4.set_title('Proporsi Pengguna Casual vs Registered', fontsize=15)
ax4.axis('equal')
st.pyplot(fig4)

# Visualisasi 5: Clustering Pola Penggunaan Sepeda
st.header("Clustering Pola Penggunaan Sepeda")
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

X = hour_data[['hr', 'cnt']]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=3)
hour_data['cluster'] = kmeans.fit_predict(X_scaled)

fig5, ax5 = plt.subplots(figsize=(12, 6))
sns.scatterplot(x='hr', y='cnt', hue='cluster', data=hour_data, palette='viridis', ax=ax5)
ax5.set_title('Clustering Pola Penggunaan Sepeda', fontsize=15)
ax5.set_xlabel('Jam', fontsize=12)
ax5.set_ylabel('Jumlah Penyewaan', fontsize=12)
st.pyplot(fig5)

# Kesimpulan
st.header("Kesimpulan")
st.markdown("""
    - **Pola Penggunaan Sepeda**: Penggunaan sepeda dipengaruhi oleh waktu (jam, hari) dan cuaca.
    - **Pengguna Casual vs Registered**: Pengguna registered mendominasi (81.2%), sedangkan pengguna casual lebih aktif di akhir pekan.
""")