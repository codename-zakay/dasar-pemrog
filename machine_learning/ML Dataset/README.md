# 🤖 Machine Learning Klasifikasi dengan Excel

Program machine learning untuk klasifikasi menggunakan dataset Excel dengan frontend Streamlit.

## 📋 Fitur

- ✅ Upload dataset dari file Excel (.xlsx, .xls)
- ✅ Preprocessing data otomatis (handle missing values, encoding)
- ✅ Multiple algoritma klasifikasi:
  - 🌲 Random Forest
  - 🔷 Support Vector Machine (SVM)
  - 📊 Naive Bayes
  - 🌳 Decision Tree
- ✅ Evaluasi model dengan confusion matrix dan classification report
- ✅ Prediksi data baru melalui web interface
- ✅ Visualisasi hasil

## 🚀 Instalasi

1. Install dependencies:
```bash
pip install -r requirements.txt
```

Atau install manual:
```bash
pip install pandas numpy scikit-learn matplotlib seaborn streamlit openpyxl xlrd
```

## 💻 Cara Menggunakan

### 1. Menggunakan Frontend Streamlit (Recommended)

Jalankan aplikasi web:
```bash
streamlit run "Machine Learning/ML Dataset/app.py"
```

Atau jika sudah di folder `ML Dataset`:
```bash
streamlit run app.py
```

Aplikasi akan terbuka di browser (biasanya di `http://localhost:8501`)

**Langkah-langkah:**
1. Buka halaman **"📤 Upload & Train"**
2. Upload file Excel Anda
3. Pilih kolom target (yang ingin diprediksi)
4. Pilih algoritma model
5. Klik **"🚀 Train Model"**
6. Setelah training selesai, gunakan halaman **"🔮 Prediksi"** untuk prediksi data baru

### 2. Menggunakan Script Python Langsung

Jalankan script `data_set.py`:
```bash
python "Machine Learning/ML Dataset/data_set.py"
```

Pastikan file Excel ada di folder yang sama dengan script, atau edit path file di dalam script.

## 📊 Format Dataset Excel

Dataset Excel harus memiliki:
- **Kolom features**: kolom-kolom yang digunakan untuk prediksi
- **Kolom target**: kolom yang ingin diprediksi (biasanya kolom terakhir)

**Contoh struktur:**
| Feature1 | Feature2 | Feature3 | Target |
|----------|----------|----------|--------|
| 10.5     | 20.3     | 5.2      | A      |
| 12.1     | 18.7     | 6.1      | B      |
| ...      | ...      | ...      | ...    |

## 🎯 Contoh Penggunaan

### Contoh 1: Training dari Excel
```python
from data_set import MLClassifier

ml = MLClassifier()
df = ml.load_excel("dataset.xlsx", target_column="kelas")
X, y, df_processed = ml.preprocess_data(df)
results = ml.train_model(X, y, model_type='random_forest')
ml.save_model('model.pkl')
```

### Contoh 2: Prediksi dengan Model yang Sudah Disimpan
```python
from data_set import MLClassifier

ml = MLClassifier()
ml.load_model('model.pkl')
prediction = ml.predict(X_new)
```

## 📁 Struktur File

```
ML Dataset/
├── data_set.py          # Script ML klasifikasi (standalone)
├── app.py              # Frontend Streamlit
├── README.md           # Dokumentasi ini
└── dataset.xlsx        # File Excel dataset Anda
```

## ⚙️ Konfigurasi

### Pilih Algoritma Model

- **Random Forest**: Bagus untuk dataset besar, robust terhadap overfitting
- **SVM**: Bagus untuk dataset kecil-menengah, non-linear patterns
- **Naive Bayes**: Cepat, bagus untuk dataset besar dengan banyak features
- **Decision Tree**: Mudah diinterpretasi, bagus untuk understanding data

### Tips

1. **Preprocessing**: Program akan otomatis:
   - Mengisi missing values dengan median (numerik) atau mode (kategorikal)
   - Encoding variabel kategorikal
   - Normalisasi data

2. **Kolom Target**: 
   - Bisa numerik atau kategorikal
   - Jika kategorikal, akan di-encode otomatis

3. **Test Size**: 
   - Default: 20% data untuk testing
   - Bisa diubah di frontend atau script

## 🐛 Troubleshooting

### Error: "File Excel tidak ditemukan"
- Pastikan file Excel ada di folder yang benar
- Periksa nama file (case-sensitive)

### Error: "Model belum di-train"
- Pastikan sudah melakukan training terlebih dahulu
- Di frontend, pastikan sudah klik tombol "Train Model"

### Error saat install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 📝 Catatan

- Model yang sudah di-train akan disimpan di session (frontend) atau file .pkl (script)
- Untuk dataset besar, training mungkin memakan waktu
- Pastikan dataset sudah bersih dan siap digunakan

## 👨‍💻 Kontributor

Dibuat untuk pembelajaran Machine Learning dengan Python.

---

**Selamat Mencoba! 🚀**

