# Bike Sharing Analysis Dashboard 🚴‍♂️📊

## Tentang Proyek

Dashboard ini merupakan hasil analisis mendalam terhadap dataset penyewaan sepeda (bike sharing) yang mencakup data dari tahun 2011-2012. Proyek ini bertujuan untuk:

1.  Memahami pola penggunaan sepeda berdasarkan faktor waktu (jam, hari, bulan, musim) dan cuaca.
2.  Menganalisis perbedaan karakteristik antara pengguna casual dan registered.
3.  Memberikan rekomendasi bisnis berbasis data untuk meningkatkan layanan.

Dashboard dibangun menggunakan **Streamlit** dengan visualisasi interaktif dari **Matplotlib** dan **Seaborn**.

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

### 1. **Analisis Berdasarkan Waktu** ⏰

- Visualisasi rata-rata penyewaan per jam, per hari dalam seminggu, per bulan, dan per musim.
- Heatmap interaktif jam vs hari dalam seminggu, jam vs bulan, Jam vs Musim untuk melihat pola gabungan.

### 2. **Analisis Berdasarkan Cuaca** ☀️🌧️

- Dampak kondisi cuaca terhadap jumlah penyewaan.
- Heatmap jam vs kondisi cuaca.

### 3. **Analisis Berdasarkan Pengguna** 👥

- Proporsi pengguna casual vs registered.
- Perbandingan pola penggunaan casual vs registered berdasarkan hari kerja/akhir pekan, jam, dan musim.

### 4. **Analisis Lanjutan** 🔬

- Segmentasi pengguna berdasarkan waktu penggunaan (Pagi, Siang, Sore, Malam) dengan analisis rata-rata penyewaan, komposisi pengguna, suhu, dan proporsi kondisi cuaca per segmen.

### 5. **Fitur Interaktif** 🎛️

- Filter data berdasarkan:
  - Rentang tanggal
  - Tahun
  - Musim
  - Kondisi cuaca
  - Jenis pengguna (Semua, Casual, atau Registered)

---

## Cara Menjalankan Dashboard

### Prasyarat

- Python 3.7+
- Pip

### Langkah-langkah

1.  **Clone repositori** (Jika proyek Anda ada di Git) atau ekstrak file ZIP proyek Anda.

2.  **Buka terminal atau command prompt**, navigasi ke direktori utama proyek (`submission`).

3.  **Buat dan aktifkan environment virtual** (direkomendasikan):

    ```bash
    python -m venv venv
    # Untuk Windows:
    venv\Scripts\activate
    # Untuk MacOS/Linux:
    source venv/bin/activate
    ```

4.  **Install dependensi**:
    Pastikan Anda berada di direktori utama proyek (`submission`) yang berisi file `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```

5.  **Jalankan aplikasi Streamlit**:
    Dari direktori utama proyek (`submission`), jalankan perintah:

    ```bash
    streamlit run dashboard/dashboard.py
    ```

6.  **Akses dashboard** di browser Anda. Streamlit akan secara otomatis membuka tab baru, atau Anda dapat mengaksesnya melalui URL yang ditampilkan di terminal (biasanya `http://localhost:8501`).

---

## Kesimpulan dan Rekomendasi Bisnis (dari Notebook)

### **Kesimpulan Analisis**

1.  **Pola Waktu**:

    - Puncak penggunaan pada jam 8 pagi dan 17-18 sore (komuter).
    - Akhir pekan menunjukkan pola rekreasi (siang-sore).
    - Musim Gugur (Fall) adalah musim puncak penyewaan.

2.  **Pengaruh Cuaca**:

    - Cuaca cerah ("Clear/Few clouds") ideal untuk penyewaan.
    - Hujan/salju lebat ("Heavy Rain/Snow/Fog") sangat mengurangi penggunaan.

3.  **Perbedaan Pengguna**:
    - Registered users (81.2%) mendominasi, terutama untuk komuting hari kerja.
    - Casual users (18.8%) lebih aktif di akhir pekan dan musim hangat, serta lebih sensitif cuaca.

### **Rekomendasi Bisnis**

1.  **Optimalisasi Operasional & Penargetan Pengguna**:

    - Sesuaikan ketersediaan sepeda pada jam sibuk komuter dan akhir pekan di area rekreasi.
    - Tawarkan paket/diskon spesifik untuk segmen waktu dan pengguna (misal, paket komuter, weekend pass, diskon makan siang).

2.  **Program Loyalitas & Konversi Pengguna**:

    - Insentif untuk konversi pengguna casual menjadi registered.
    - Tingkatkan program loyalitas registered (misal, tingkatan keanggotaan).

3.  **Inisiatif Musiman & Berbasis Cuaca**:

    - Promosi maksimal di musim ramai (Gugur & Panas) dan strategi khusus untuk musim sepi.
    - Integrasikan prediksi cuaca di aplikasi, tawarkan "Rain Guarantee".

4.  **Strategi Penempatan & Alokasi Armada**:
    - Gunakan data heatmap (jam vs hari/bulan/musim) untuk optimasi penempatan armada.

---

## Teknologi yang Digunakan

- **Python** (Pandas) untuk manipulasi dan analisis data.
- **Matplotlib** & **Seaborn** untuk visualisasi data.
- **Streamlit** untuk membangun dashboard interaktif.
- **Calendar** (library Python standar).

---

## Detail Pembuat

- **Nama**: Muhammad Husain Fadhlillah
- **Email**: mc006d5y2343@student.devacademy.id
- **ID Dicoding**: MC006D5Y2343
