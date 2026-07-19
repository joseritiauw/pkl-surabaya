# Peta Interaktif Keadilan Spasial Akses Bahan Baku PKL Surabaya

Project WebGIS ini merupakan pemenuhan Tugas Akhir Semester (UAS) mata kuliah Sistem Informasi Geografis Universitas Mercu Buana. 
Aplikasi ini dibangun menggunakan pendekatan Low-Code dengan **Python, Streamlit, dan Folium**, serta menggunakan data spasial berbasis **GeoPackage (.gpkg)**.

Tujuan utama dari website ini adalah untuk menampilkan hasil analisis spasial mengenai tingkat keadilan dan aksesibilitas Pedagang Kaki Lima (PKL) terhadap pasar tradisional di Kota Surabaya, serta merekomendasikan lokasi "Pasar Satelit" berdasarkan area *blank spot*.

## 🚀 Fitur Utama
- **Visualisasi Interaktif:** Peta disajikan secara interaktif menggunakan Folium dengan dukungan Fullscreen, MiniMap, dan Scale Bar.
- **Analisis Clustering (K-Means):** Algoritma *K-Means Clustering* dari *scikit-learn* digunakan secara otomatis (saat aplikasi berjalan) untuk menentukan 3 lokasi optimal pembangunan Pasar Satelit berdasarkan konsentrasi PKL di area *blank spot*.
- **Desain Modern:** Memiliki Executive Summary dan Sidebar yang rapi, informatif, dan responsif.
- **Robust & Fleksibel:** Kode telah dilengkapi dengan error-handling dan pembacaan atribut secara dinamis untuk beradaptasi terhadap variasi struktur tabel di dataset.

## 🛠️ Prasyarat & Instalasi

Pastikan Anda memiliki Python versi 3.8 ke atas terinstall di komputer Anda. Disarankan untuk menggunakan virtual environment.

1. Buka terminal atau command prompt pada folder project.
2. Install semua dependensi yang diperlukan dengan menjalankan perintah berikut:

```bash
pip install -r requirements.txt
```

*(Dependensi utama meliputi: streamlit, folium, streamlit-folium, geopandas, pandas, numpy, scikit-learn, shapely, dan library spasial pendukung lainnya.)*

## 💻 Cara Menjalankan Secara Lokal

Setelah instalasi selesai, Anda dapat langsung menjalankan aplikasi melalui Streamlit:

```bash
streamlit run app.py
```

Perintah ini akan secara otomatis membuka tab baru di browser Anda yang menampilkan aplikasi WebGIS.

## 🌐 Cara Deploy ke Streamlit Community Cloud

Aplikasi ini sudah dipersiapkan dan siap di-*deploy* ke [Streamlit Community Cloud](https://streamlit.io/cloud) secara gratis. Ikuti langkah-langkah berikut:

1. **Upload ke GitHub:**
   - Buat repositori baru di akun GitHub Anda.
   - Upload seluruh folder project (termasuk `app.py`, `requirements.txt`, dan folder `Data` beserta isinya) ke repositori tersebut.
2. **Deploy di Streamlit Cloud:**
   - Buka [share.streamlit.io](https://share.streamlit.io) dan login menggunakan akun GitHub Anda.
   - Klik tombol **"New app"**.
   - Pilih repositori GitHub yang baru saja Anda buat.
   - Pilih branch utama (biasanya `main` atau `master`).
   - Pada bagian *Main file path*, ketik `app.py`.
   - Klik tombol **"Deploy!"**.
3. Selesai! Dalam beberapa menit, aplikasi WebGIS Anda akan online dan dapat diakses dari mana saja melalui URL yang diberikan oleh Streamlit.
