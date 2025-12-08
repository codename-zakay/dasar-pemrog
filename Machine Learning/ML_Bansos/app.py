# app.py

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

# ============================
# 1. SETTING PAGE STREAMLIT
# ============================
st.set_page_config(page_title="Prediksi Penerima Bantuan Sosial", page_icon="🏠", layout="wide")
st.title("🔍 Prediksi Keluarga yang Belum Menerima Bantuan Sosial")
st.markdown("Aplikasi ini menggunakan **Machine Learning (Random Forest)** untuk memprediksi keluarga yang belum menerima bantuan sosial berdasarkan data usulan.")

# ============================
# 2. FUNGSI UNTUK MEMPROSES DATA
# ============================
def preprocess_data(df):
    """
    Membersihkan dan mempersiapkan data untuk model.
    """
    df = df.copy()
    
    # Hapus baris kosong (jika ada)
    df.dropna(subset=['Nama', 'Klaster'], inplace=True)
    
    # Isi missing value dengan modus/median
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else '', inplace=True)
        else:
            df[col].fillna(df[col].median() if df[col].dtype != 'object' else 0, inplace=True)
    
    return df

def prepare_features(df):
    """
    Membuat fitur untuk model dari data yang ada.
    Karena tidak ada fitur numerik yang jelas, kita buat fitur sederhana:
    - Jumlah kata dalam alamat (sebagai proxy kerumitan lokasi)
    - Panjang NIK (sebagai proxy validitas data)
    - Encoding Klaster
    """
    df_features = df.copy()
    
    # Fitur 1: Panjang alamat (jumlah kata)
    df_features['Panjang_Alamat'] = df_features['Alamat Lengkap'].apply(lambda x: len(str(x).split()))
    
    # Fitur 2: Panjang NIK
    df_features['Panjang_NIK'] = df_features['NIK'].apply(lambda x: len(str(x)))
    
    # Fitur 3: Encoding Klaster
    le = LabelEncoder()
    df_features['Klaster_Encoded'] = le.fit_transform(df_features['Klaster'])
    
    # Fitur 4: Apakah ada nomor KK? (1 jika ada, 0 jika tidak)
    df_features['Ada_KK'] = df_features['No KK'].apply(lambda x: 1 if pd.notna(x) and str(x).strip() != '' else 0)
    
    return df_features[['Panjang_Alamat', 'Panjang_NIK', 'Klaster_Encoded', 'Ada_KK']]

# ============================
# 3. FUNGSI UNTUK MEMBUAT DATA SIMULASI TARGET
# ============================
def create_simulation_target(df):
    """
    Karena data asli tidak memiliki kolom target (sudah/belum dapat bantuan),
    kita buat simulasi untuk keperluan demo.
    Aturan simulasi:
    - 70% data diberi label 1 (sudah dapat) secara acak
    - 30% data diberi label 0 (belum dapat)
    - Prioritas berdasarkan: Klaster Lansia & Anak lebih tinggi
    """
    np.random.seed(42)  # Untuk hasil konsisten
    
    # Beri bobot berdasarkan klaster
    conditions = [
        df['Klaster'].str.contains('Lansia', na=False),
        df['Klaster'].str.contains('Anak', na=False),
        df['Klaster'].str.contains('Disabilitas', na=False)
    ]
    choices = [0.8, 0.7, 0.6]  # Probabilitas tinggi untuk dapat bantuan
    default_prob = 0.3
    
    prob = np.select(conditions, choices, default=default_prob)
    
    # Hasilkan label acak berdasarkan probabilitas
    y = np.random.binomial(1, prob, size=len(df))
    
    return y

# ============================
# 4. FUNGSI UNTUK MELATIH MODEL
# ============================
def train_model(X, y):
    """
    Melatih model Random Forest dengan data fitur (X) dan target (y).
    """
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Inisialisasi model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42,
        class_weight='balanced'  # Handle imbalance
    )
    
    # Training
    model.fit(X_train, y_train)
    
    # Evaluasi
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    return model, acc

# ============================
# 5. INTERFACE STREAMLIT
# ============================

# Upload file
uploaded_file = st.file_uploader("📂 Upload file Excel data usulan bantuan", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Baca file
        df = pd.read_excel(uploaded_file)
        
        # Tampilkan data asli
        st.subheader("📊 Data Usulan Bantuan")
        st.dataframe(df.head(10), use_container_width=True)
        st.caption(f"Total data: {len(df)} baris, {len(df.columns)} kolom")
        
        # Proses data
        with st.spinner("🔄 Memproses data..."):
            df_clean = preprocess_data(df)
            X = prepare_features(df_clean)
            y = create_simulation_target(df_clean)
        
        # Info fitur
        with st.expander("🔍 Lihat fitur yang digunakan untuk prediksi"):
            st.dataframe(X.head(), use_container_width=True)
            st.markdown("""
            **Penjelasan Fitur:**
            1. **Panjang_Alamat**: Jumlah kata dalam alamat (indikasi kelengkapan data).
            2. **Panjang_NIK**: Panjang NIK (indikasi validitas data).
            3. **Klaster_Encoded**: Klaster penerima (Lansia, Anak, dll) dalam bentuk angka.
            4. **Ada_KK**: 1 jika nomor KK ada, 0 jika tidak.
            """)
        
        # Latih model
        with st.spinner("🤖 Melatih model Random Forest..."):
            model, accuracy = train_model(X, y)
            
        st.success(f"✅ Model berhasil dilatih! Akurasi: {accuracy:.2%}")
        
        # Prediksi untuk semua data
        predictions = model.predict(X)
        df_clean['Prediksi_Status'] = predictions
        df_clean['Prediksi_Status_Label'] = df_clean['Prediksi_Status'].map({1: 'Sudah', 0: 'Belum'})
        
        # Hitung statistik
        belum_count = (predictions == 0).sum()
        sudah_count = (predictions == 1).sum()
        
        # Tampilkan hasil
        col1, col2 = st.columns(2)
        with col1:
            st.metric("👥 Diprediksi BELUM dapat bantuan", f"{belum_count} keluarga")
        with col2:
            st.metric("✅ Diprediksi SUDAH dapat bantuan", f"{sudah_count} keluarga")
        
        # Tampilkan yang diprediksi belum dapat bantuan
        st.subheader("🏠 Keluarga yang Diprediksi BELUM Menerima Bantuan")
        df_belum = df_clean[df_clean['Prediksi_Status'] == 0]
        
        if len(df_belum) > 0:
            # Pilih kolom yang relevan untuk ditampilkan
            display_cols = ['No', 'Nama', 'NIK', 'No KK', 'Klaster', 'Usulan', 'Alamat Lengkap', 'Prediksi_Status_Label']
            display_cols = [col for col in display_cols if col in df_belum.columns]
            
            st.dataframe(df_belum[display_cols], use_container_width=True)
            
            # Tombol download
            csv = df_belum.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download data (CSV)",
                data=csv,
                file_name="keluarga_belum_dapat_bantuan.csv",
                mime="text/csv",
            )
        else:
            st.info("🎉 Semua keluarga diprediksi sudah menerima bantuan!")
        
        # Visualisasi sederhana
        st.subheader("📈 Distribusi Prediksi per Klaster")
        chart_data = df_clean.groupby(['Klaster', 'Prediksi_Status_Label']).size().unstack(fill_value=0)
        st.bar_chart(chart_data)
        
        # Feature importance
        st.subheader("🔝 Tingkat Kepentingan Fitur")
        feature_names = X.columns
        importances = model.feature_importances_
        importance_df = pd.DataFrame({
            'Fitur': feature_names,
            'Importance': importances
        }).sort_values('Importance', ascending=False)
        
        st.dataframe(importance_df, use_container_width=True)
        
        # Catatan penting
        st.info("""
        **⚠️ Catatan Penting:**
        1. Data target (sudah/belum dapat bantuan) dibuat **secara simulasi** karena tidak ada dalam data asli.
        2. Model ini adalah **contoh demonstrasi** dan belum tentu akurat untuk penggunaan nyata.
        3. Untuk implementasi sebenarnya, diperlukan data riil status penerimaan bantuan.
        4. Konsultasikan dengan pakar sosial sebelum mengambil keputusan nyata.
        """)
        
    except Exception as e:
        st.error(f"❌ Terjadi kesalahan: {str(e)}")
        st.write("Pastikan file Excel memiliki format yang sesuai dengan contoh.")

else:
    # Tampilkan panduan jika belum upload file
    st.markdown("""
    ### 📋 Panduan Penggunaan:
    
    1. **Siapkan file Excel** dengan format seperti contoh di bawah.
    2. **Upload file** melalui menu di atas.
    3. **Model akan dilatih** secara otomatis.
    4. **Lihat hasil prediksi** keluarga yang belum menerima bantuan.
    
    ### 🗂️ Format Excel yang Disarankan:
    
    | No | Nama | NIK | No KK | Alamat Lengkap | Klaster | Usulan |
    |----|------|-----|-------|----------------|---------|--------|
    | 1  | ...  | ... | ...   | ...            | Lansia  | ...    |
    | 2  | ...  | ... | ...   | ...            | Anak    | ...    |
    
    ### 🔧 Teknologi yang Digunakan:
    - **Python** dengan **scikit-learn** (Random Forest)
    - **Streamlit** untuk antarmuka web
    - **Pandas** untuk pengolahan data
    """)
    
    # Contoh data minimal
    example_data = {
        'No': [1, 2, 3],
        'Nama': ['Hairiah', 'Rahmat Al Khoirul', 'Diyon'],
        'NIK': ['3216064304680020', '3216061201150013', '3212232911030003'],
        'No KK': ['3216061111100180', '3216060603230030', '3212230206099955'],
        'Alamat Lengkap': ['Kp. Pulo Rt 001 Rw 035', 'Kp. Pulo Rt 001 Rw 036', 'Bekasi Regensi I Rt 004 Rw 005'],
        'Klaster': ['Lansia', 'Anak', 'Anak'],
        'Usulan': ['Kebutuhan Lansia', 'ATK, Kebutuhan Pendidikan', 'ATK, Kebutuhan Pendidikan']
    }
    
    st.dataframe(pd.DataFrame(example_data), use_container_width=True)