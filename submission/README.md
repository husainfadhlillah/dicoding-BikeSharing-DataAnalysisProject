# Bike Sharing Dashboard 🚴‍♂️📊

## Tentang Dashboard

Dashboard ini dirancang untuk menganalisis data Bike Sharing Dataset. Dashboard menampilkan visualisasi interaktif yang mencakup:

- Pola penggunaan sepeda berdasarkan waktu (jam, hari, bulan, musim).
- Pengaruh cuaca terhadap penyewaan sepeda.
- Perbandingan antara pengguna casual dan registered.
- Clustering pola penggunaan sepeda.

Dashboard ini dibangun menggunakan **Streamlit** dan memanfaatkan library Python seperti **Pandas**, **Matplotlib**, **Seaborn**, dan **Plotly**.

---

## Cara Menjalankan Dashboard 🚀

### 1. **Persiapan Lingkungan**

Pastikan Anda telah menginstall Python (versi 3.7 atau lebih baru) dan pip. Jika belum, Anda bisa mengunduhnya dari [situs resmi Python](https://www.python.org/).

#### **Menggunakan Anaconda (Opsional)**

Jika Anda menggunakan Anaconda, buat environment baru dengan perintah berikut:

```bash
conda create --name bike-sharing python=3.9
conda activate bike-sharing
```

---

### 2. **Install Dependensi**

Install semua library yang diperlukan dengan menjalankan perintah berikut:

```bash
pip install streamlit pandas matplotlib seaborn plotly scikit-learn
```

---

### 3. **Struktur Folder**

Pastikan struktur folder Anda seperti ini:

```
submission
├───dashboard
| ├───day_data_clean.csv
| ├───hour_data_clean.csv
| ├───requirements.txt
| └───dashboard.py
├───data
| ├───day.csv
| └───hour.csv
├───notebook.ipynb
├───rangkuman.txt
├───README.md
└───url.txt
```

- File `hour_data_clean.csv` dan `day_data_clean.csv` harus berada di folder `main_data`.
- File `dashboard.py` adalah file utama yang berisi kode Streamlit.

---

### 4. **Menjalankan Dashboard**

1. Buka terminal atau command prompt.
2. Arahkan ke folder tempat `dashboard.py` berada:

   ```bash
   cd /path/to/submission
   ```

   Ganti `/path/to/submission` dengan path sebenarnya ke folder Anda.

3. Jalankan dashboard dengan perintah:

   ```bash
   streamlit run dashboard.py
   ```

4. Dashboard akan terbuka di browser secara otomatis. Jika tidak, buka URL yang ditampilkan di terminal (biasanya `http://localhost:8501`).

---

### 5. **Filter Data**

Di sidebar dashboard, Anda dapat memfilter data berdasarkan:

- **Tahun**: Pilih tahun tertentu atau tampilkan semua data.
- **Musim**: Pilih musim tertentu atau tampilkan semua musim.

---

## Visualisasi yang Tersedia 📈

1. **Pola Penggunaan Sepeda berdasarkan Jam**:

   - Menampilkan rata-rata penyewaan sepeda per jam.
   - Terlihat pola penggunaan tertinggi pada jam 8 pagi dan 17-18 sore.

2. **Pengaruh Cuaca terhadap Penyewaan Sepeda**:

   - Menampilkan rata-rata penyewaan berdasarkan kondisi cuaca.
   - Kondisi cuaca cerah (Clear/Few clouds) memiliki penyewaan tertinggi.

3. **Heatmap Jam vs Hari**:

   - Menampilkan heatmap penggunaan sepeda berdasarkan jam dan hari.
   - Terlihat pola penggunaan yang berbeda antara hari kerja dan akhir pekan.

4. **Proporsi Pengguna Casual vs Registered**:

   - Menampilkan perbandingan antara pengguna casual dan registered.
   - Pengguna registered mendominasi dengan proporsi 81.2%.

5. **Clustering Pola Penggunaan Sepeda**:
   - Menampilkan clustering pola penggunaan sepeda berdasarkan jam dan jumlah penyewaan.

---

## Kesimpulan 🎯

- **Pola Penggunaan Sepeda**: Penggunaan sepeda dipengaruhi oleh waktu (jam, hari) dan cuaca.
- **Pengguna Casual vs Registered**: Pengguna registered mendominasi (81.2%), sedangkan pengguna casual lebih aktif di akhir pekan.

---

## Troubleshooting ⚠️

Jika Anda mengalami masalah saat menjalankan dashboard, pastikan:

1. File CSV (`hour_data_clean.csv` dan `day_data_clean.csv`) ada di folder `main_data`.
2. Semua dependensi telah terinstall dengan benar.
3. Anda menjalankan perintah `streamlit run dashboard.py` dari folder yang benar.
