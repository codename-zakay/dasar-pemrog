# 🚀 Cara Menjalankan Program

Panduan lengkap untuk menjalankan aplikasi Machine Learning Klasifikasi.

## 📋 Prasyarat

Pastikan Python sudah terinstall di komputer Anda. Cek dengan:
```bash
python --version
```
atau
```bash
python3 --version
```

## 🔧 Langkah 1: Install Dependencies

Buka terminal/command prompt di folder project, lalu jalankan:

### Windows:
```bash
pip install -r requirements.txt
```

### Mac/Linux:
```bash
pip3 install -r requirements.txt
```

**Atau install manual:**
```bash
pip install pandas numpy scikit-learn matplotlib seaborn streamlit openpyxl xlrd
```

## 🎯 Langkah 2: Menjalankan Aplikasi

### **Cara 1: Menggunakan File Batch (Paling Mudah - Windows)**

1. Double-click file **`run.bat`** di folder `ML Dataset`
2. Aplikasi akan otomatis terbuka di browser

### **Cara 2: Menggunakan Command Line**

#### Windows (Command Prompt atau PowerShell):
```bash
cd "Machine Learning\ML Dataset"
streamlit run app.py
```

#### Mac/Linux:
```bash
cd "Machine Learning/ML Dataset"
streamlit run app.py
```

### **Cara 3: Menggunakan Terminal di VS Code/Cursor**

1. Buka terminal di VS Code/Cursor (Ctrl + ` atau Terminal > New Terminal)
2. Navigate ke folder:
   ```bash
   cd "Machine Learning/ML Dataset"
   ```
3. Jalankan:
   ```bash
   streamlit run app.py
   ```

## 🌐 Langkah 3: Menggunakan Aplikasi

Setelah menjalankan command, akan muncul:
- URL lokal: `http://localhost:8501`
- Aplikasi akan otomatis terbuka di browser default Anda

Jika tidak terbuka otomatis, copy URL yang muncul di terminal dan buka di browser.

## 📱 Fitur Aplikasi

### Halaman 1: 📤 Upload & Train
1. Klik **"Browse files"** atau drag & drop file Excel Anda
2. Pilih **kolom target** (yang ingin diprediksi)
3. Pilih **algoritma model** (Random Forest, SVM, dll)
4. Atur **proporsi data test** (default: 20%)
5. Klik **"🚀 Train Model"**
6. Tunggu proses training selesai
7. Lihat hasil: akurasi, classification report, dan confusion matrix

### Halaman 2: 🔮 Prediksi
1. Setelah model di-train, pindah ke halaman **"🔮 Prediksi"**
2. Isi form dengan data yang ingin diprediksi
3. Klik **"🔮 Prediksi"**
4. Lihat hasil prediksi dan probabilitas

### Halaman 3: 📊 Info Model
- Lihat informasi model yang sudah di-train
- Lihat feature importance (jika menggunakan Random Forest)
- Lihat daftar fitur yang digunakan

## 🖥️ Menjalankan Script Python Langsung (Tanpa Frontend)

Jika ingin menggunakan script Python langsung tanpa frontend:

```bash
cd "Machine Learning\ML Dataset"
python data_set.py
```

**Catatan:** Pastikan file Excel ada di folder yang sama dengan `data_set.py`

## ⚠️ Troubleshooting

### Error: "streamlit: command not found"
**Solusi:** Install streamlit terlebih dahulu
```bash
pip install streamlit
```

### Error: "No module named 'pandas'"
**Solusi:** Install semua dependencies
```bash
pip install -r requirements.txt
```

### Error: "File Excel tidak ditemukan"
**Solusi:** 
- Pastikan file Excel ada di folder `ML Dataset`
- Atau edit path file di script `data_set.py`

### Port sudah digunakan (Error: Port 8501 already in use)
**Solusi:** 
- Tutup aplikasi yang menggunakan port 8501
- Atau jalankan dengan port lain:
```bash
streamlit run app.py --server.port 8502
```

### Browser tidak terbuka otomatis
**Solusi:**
- Copy URL yang muncul di terminal (biasanya `http://localhost:8501`)
- Paste di browser manual

## 📝 Contoh Dataset Excel

Format dataset yang didukung:
- File Excel (.xlsx atau .xls)
- Kolom pertama sampai kedua terakhir: Features (data untuk prediksi)
- Kolom terakhir: Target (yang ingin diprediksi)

**Contoh struktur:**
| Feature1 | Feature2 | Feature3 | Target |
|----------|----------|----------|--------|
| 10.5     | 20.3     | 5.2      | A      |
| 12.1     | 18.7     | 6.1      | B      |

## 🎓 Tips

1. **Dataset Besar:** Jika dataset sangat besar, training mungkin memakan waktu. Sabar ya! 😊
2. **Kolom Target:** Pilih kolom yang memang ingin diprediksi (bukan ID atau kolom yang tidak relevan)
3. **Missing Values:** Program akan otomatis mengisi missing values, tapi lebih baik data sudah bersih
4. **Save Model:** Model yang di-train di frontend tersimpan di session. Untuk save permanen, gunakan script `data_set.py`

## 🆘 Butuh Bantuan?

Jika ada masalah:
1. Pastikan semua dependencies sudah terinstall
2. Cek versi Python (disarankan Python 3.8+)
3. Pastikan file Excel formatnya benar
4. Cek error message di terminal untuk detail

---

**Selamat Mencoba! 🚀**

