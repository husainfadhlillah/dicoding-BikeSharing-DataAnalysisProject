# Bike Sharing Analysis Dashboard 🚴‍♂️📊

## Tentang Proyek

Dashboard ini merupakan hasil analisis mendalam terhadap dataset penyewaan sepeda (bike sharing) yang mencakup data dari tahun 2011-2012. Proyek ini bertujuan untuk:

1. Memahami pola penggunaan sepeda berdasarkan faktor waktu dan cuaca
2. Menganalisis perbedaan karakteristik antara pengguna casual dan registered
3. Memberikan rekomendasi bisnis berbasis data untuk meningkatkan layanan

Dashboard dibangun menggunakan **Streamlit** dengan visualisasi interaktif dari **Matplotlib**, **Seaborn**, dan **Plotly**.

---

## Struktur Proyek

```
submission
├───dashboard
│   ├───day_data_clean.csv       # Data harian yang sudah dibersihkan
│   ├───hour_data_clean.csv      # Data per jam yang sudah dibersihkan
│   └───dashboard.py             # Kode utama dashboard Streamlit
├───data
│   ├───day.csv                  # Dataset harian mentah
│   └───hour.csv                 # Dataset per jam mentah
├───notebook.ipynb               # Notebook analisis lengkap
├───README.md                    # Dokumen ini
├───requirements.txt             # Daftar dependensi
└───url.txt                      # Sumber dataset
```

---

## Fitur Utama Dashboard

### 1. **Analisis Temporal** ⏰

- Pola penggunaan per jam dengan puncak pada jam 8 pagi (347.6 ± 58.2 penyewaan/jam) dan 17-18 sore (468.3 ± 58.2 penyewaan/jam)
- Heatmap interaktif jam vs hari yang menunjukkan perbedaan pola weekday vs weekend
- Analisis musiman dengan performa terbaik di musim gugur (Fall)

### 2. **Analisis Pengaruh Cuaca** ☀️🌧️

- Dampak kondisi cuaca terhadap jumlah penyewaan
- Cuaca cerah menghasilkan 205.4 penyewaan/jam (SD=112.3)
- Heavy Rain mengurangi penyewaan hingga 63.4%

### 3. **Segmentasi Pengguna** 👥

- Proporsi pengguna: 81.2% registered vs 18.8% casual
- Analisis RFM (Recency, Frequency, Monetary) untuk pengguna registered
- Clustering pengguna berdasarkan intensitas penggunaan

### 4. **Fitur Interaktif** 🎛️

- Filter data berdasarkan:
  - Rentang tanggal (2011-01-01 hingga 2012-12-31)
  - Tahun (2011 atau 2012)
  - Musim (Spring, Summer, Fall, Winter)
  - Kondisi cuaca
  - Jenis pengguna (Semua, Casual, atau Registered)

---

## Cara Menjalankan Dashboard

### Prasyarat

- Python 3.7+
- Pip atau Conda

### Langkah-langkah

1. **Clone repositori**

   ```bash
   git clone [URL_REPOSITORI]
   cd submission
   ```

2. **Buat environment virtual (opsional)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependensi**

   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan dashboard**

   ```bash
   streamlit run dashboard/dashboard.py
   ```

5. **Akses dashboard** di browser:
   ```
   http://localhost:8501
   ```

---

## Temuan Utama dan Rekomendasi

### 🔍 Temuan Kunci

1. **Pola Waktu**:

   - Pola commuting jelas terlihat pada jam sibuk
   - Weekend menunjukkan pola berbeda dengan puncak siang hari

2. **Pengaruh Cuaca**:

   - Suhu optimal: 20-25°C
   - Cuaca buruk berdampak lebih besar pada pengguna casual

3. **Segmentasi Pengguna**:
   - Pengguna registered adalah backbone bisnis (stabilitas pendapatan)
   - Pengguna casual mewakili peluang pertumbuhan

### 💡 Rekomendasi Bisnis

1. **Manajemen Inventori**:

   - Tambah 40% stok pada jam sibuk (7-9 & 16-18) di hari kerja
   - Alokasi dinamis berdasarkan prediksi cuaca

2. **Strategi Pemasaran**:

   - "Weekend Warrior Package" untuk konversi casual → registered
   - Program loyalitas "Early Bird Reward"

3. **Strategi Harga**:
   - Harga premium 15% pada jam sibuk
   - Diskon 20% untuk jam sepi dan cuaca buruk

---

## Teknologi yang Digunakan

- **Python** (Pandas, NumPy) untuk pemrosesan data
- **Matplotlib** & **Seaborn** untuk visualisasi statis
- **Streamlit** untuk antarmuka dashboard
- **Scikit-learn** untuk analisis lanjutan (RFM)

---

## Kontribusi

Proyek ini dikembangkan oleh:

- **Nama**: Muhammad Husain Fadhlillah
- **Email**: mc006d5y2343@student.devacademy.id
- **ID Dicoding**: MC006D5Y2343
