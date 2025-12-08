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
def split_address_column(df):
    """
    Memisahkan kolom 'Alamat Lengkap' menjadi 4 kolom terpisah:
    - Kabupaten/Kota
    - Kecamatan
    - Desa/Kelurahan
    - Alamat Detail (Jalan/RT/RW)
    
    Jika dataframe sudah memiliki kolom terpisah, gunakan kolom tersebut.
    """
    df = df.copy()
    
    # Cek apakah kolom alamat sudah terpisah
    address_columns = ['Kabupaten/Kota', 'Kecamatan', 'Desa/Kelurahan', 'Alamat (Jalan/RT dan RW)']
    
    if 'Alamat Lengkap' in df.columns:
        # Jika masih dalam satu kolom, coba pisahkan
        # Asumsi format: "Bekasi | Tambun Selatan | Sumber Jaya | Kp. Pulo Rt 001 Rw 035"
        try:
            # Coba split dengan karakter '|' jika ada
            if df['Alamat Lengkap'].astype(str).str.contains('\|').any():
                address_parts = df['Alamat Lengkap'].astype(str).str.split('\|', expand=True)
                if address_parts.shape[1] >= 4:
                    df['Kabupaten/Kota'] = address_parts[0].str.strip()
                    df['Kecamatan'] = address_parts[1].str.strip()
                    df['Desa/Kelurahan'] = address_parts[2].str.strip()
                    df['Alamat Detail'] = address_parts[3].str.strip()
            else:
                # Jika tidak ada pemisah '|', gunakan kolom yang sudah ada atau buat default
                if all(col in df.columns for col in address_columns[:3]):
                    # Kolom sudah terpisah dalam file Excel
                    df['Kabupaten/Kota'] = df.get('Kabupaten/Kota', '')
                    df['Kecamatan'] = df.get('Kecamatan', '')
                    df['Desa/Kelurahan'] = df.get('Desa/Kelurahan', '')
                    df['Alamat Detail'] = df.get('Alamat (Jalan/RT dan RW)', df.get('Alamat Lengkap', ''))
                else:
                    # Buat kolom dengan nilai default
                    df['Kabupaten/Kota'] = 'Bekasi'  # Default dari data contoh
                    df['Kecamatan'] = 'Tambun Selatan'  # Default dari data contoh
                    df['Desa/Kelurahan'] = 'Sumber Jaya'  # Default dari data contoh
                    df['Alamat Detail'] = df['Alamat Lengkap']
        except:
            # Jika error, buat kolom dengan nilai default
            for col in ['Kabupaten/Kota', 'Kecamatan', 'Desa/Kelurahan']:
                df[col] = ''
            df['Alamat Detail'] = df['Alamat Lengkap']
    
    # Pastikan semua kolom alamat ada
    for col in ['Kabupaten/Kota', 'Kecamatan', 'Desa/Kelurahan', 'Alamat Detail']:
        if col not in df.columns:
            df[col] = ''
    
    return df

def preprocess_data(df):
    """
    Membersihkan dan mempersiapkan data untuk model.
    """
    df = df.copy()
    
    # Partisi alamat lengkap
    df = split_address_column(df)
    
    # Hapus baris kosong (jika ada)
    required_cols = ['Nama', 'Klaster']
    df.dropna(subset=required_cols, inplace=True)
    
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
    """
    df_features = df.copy()
    
    # Fitur 1: Panjang alamat detail (jumlah kata)
    df_features['Panjang_Alamat_Detail'] = df_features['Alamat Detail'].apply(lambda x: len(str(x).split()))
    
    # Fitur 2: Panjang NIK
    df_features['Panjang_NIK'] = df_features['NIK'].apply(lambda x: len(str(x)))
    
    # Fitur 3: Encoding Klaster
    le_klaster = LabelEncoder()
    df_features['Klaster_Encoded'] = le_klaster.fit_transform(df_features['Klaster'])
    
    # Fitur 4: Apakah ada nomor KK? (1 jika ada, 0 jika tidak)
    df_features['Ada_KK'] = df_features['No KK'].apply(lambda x: 1 if pd.notna(x) and str(x).strip() != '' else 0)
    
    # Fitur 5: Encoding Kabupaten
    le_kabupaten = LabelEncoder()
    df_features['Kabupaten_Encoded'] = le_kabupaten.fit_transform(df_features['Kabupaten/Kota'].fillna('Tidak Diketahui'))
    
    # Fitur 6: Encoding Kecamatan
    le_kecamatan = LabelEncoder()
    df_features['Kecamatan_Encoded'] = le_kecamatan.fit_transform(df_features['Kecamatan'].fillna('Tidak Diketahui'))
    
    # Fitur 7: Encoding Desa
    le_desa = LabelEncoder()
    df_features['Desa_Encoded'] = le_desa.fit_transform(df_features['Desa/Kelurahan'].fillna('Tidak Diketahui'))
    
    # Fitur 8: Apakah alamat mengandung RT/RW? (indikasi kelengkapan data)
    df_features['Ada_RT_RW'] = df_features['Alamat Detail'].apply(
        lambda x: 1 if 'rt' in str(x).lower() or 'rw' in str(x).lower() or 'RT' in str(x) or 'RW' in str(x) else 0
    )
    
    # Fitur 9: Jumlah kata dalam nama (proxy untuk kelengkapan data)
    df_features['Panjang_Nama'] = df_features['Nama'].apply(lambda x: len(str(x).split()))
    
    # Pilih fitur yang akan digunakan
    feature_cols = [
        'Panjang_Alamat_Detail', 'Panjang_NIK', 'Klaster_Encoded', 'Ada_KK',
        'Kabupaten_Encoded', 'Kecamatan_Encoded', 'Desa_Encoded',
        'Ada_RT_RW', 'Panjang_Nama'
    ]
    
    return df_features[feature_cols]

# ============================
# 3. FUNGSI UNTUK MEMBUAT DATA SIMULASI TARGET
# ============================
def create_simulation_target(df):
    """
    Membuat target simulasi untuk training model.
    """
    np.random.seed(42)  # Untuk hasil konsisten
    
    # Beri bobot berdasarkan klaster
    conditions = [
        df['Klaster'].str.contains('Lansia', na=False),
        df['Klaster'].str.contains('Anak', na=False),
        df['Klaster'].str.contains('Disabilitas', na=False),
        df['Klaster'].str.contains('Rentan', na=False)
    ]
    choices = [0.8, 0.7, 0.6, 0.5]  # Probabilitas tinggi untuk dapat bantuan
    default_prob = 0.3
    
    prob = np.select(conditions, choices, default=default_prob)
    
    # Tambah bobot berdasarkan kecamatan (simulasi prioritas wilayah)
    if 'Kecamatan' in df.columns:
        # Asumsikan beberapa kecamatan lebih diprioritaskan
        prior_kecamatan = ['Tambun Selatan', 'Cibitung']  # Contoh kecamatan prioritas
        mask_prior_kecamatan = df['Kecamatan'].isin(prior_kecamatan)
        prob[mask_prior_kecamatan] = np.minimum(prob[mask_prior_kecamatan] + 0.1, 0.9)
    
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
        max_depth=7,
        random_state=42,
        class_weight='balanced',
        min_samples_split=5,
        min_samples_leaf=2
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
        st.subheader("📊 Data Usulan Bantuan (Original)")
        st.dataframe(df.head(10), use_container_width=True)
        st.caption(f"Total data: {len(df)} baris, {len(df.columns)} kolom")
        
        # Proses data
        with st.spinner("🔄 Memproses data dan mempartisi alamat..."):
            df_clean = preprocess_data(df)
            
            # Tampilkan struktur alamat yang sudah dipartisi
            st.subheader("🏠 Struktur Alamat yang Sudah Dipartisi")
            address_cols = ['Nama', 'Kabupaten/Kota', 'Kecamatan', 'Desa/Kelurahan', 'Alamat Detail', 'Klaster']
            display_cols = [col for col in address_cols if col in df_clean.columns]
            st.dataframe(df_clean[display_cols].head(10), use_container_width=True)
            
            # Persiapan fitur
            X = prepare_features(df_clean)
            y = create_simulation_target(df_clean)
        
        # Info fitur
        with st.expander("🔍 Lihat fitur yang digunakan untuk prediksi"):
            st.dataframe(X.head(), use_container_width=True)
            st.markdown("""
            **Penjelasan Fitur:**
            1. **Panjang_Alamat_Detail**: Jumlah kata dalam alamat detail.
            2. **Panjang_NIK**: Panjang NIK (indikasi validitas data).
            3. **Klaster_Encoded**: Klaster penerima dalam bentuk angka.
            4. **Ada_KK**: 1 jika nomor KK ada, 0 jika tidak.
            5. **Kabupaten_Encoded**: Kabupaten dalam bentuk angka.
            6. **Kecamatan_Encoded**: Kecamatan dalam bentuk angka.
            7. **Desa_Encoded**: Desa/Kelurahan dalam bentuk angka.
            8. **Ada_RT_RW**: 1 jika alamat mengandung RT/RW, 0 jika tidak.
            9. **Panjang_Nama**: Jumlah kata dalam nama.
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
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👥 Diprediksi BELUM dapat", f"{belum_count} keluarga")
        with col2:
            st.metric("✅ Diprediksi SUDAH dapat", f"{sudah_count} keluarga")
        with col3:
            st.metric("🎯 Akurasi Model", f"{accuracy:.2%}")
        
        # Filter dan analisis berdasarkan wilayah
        st.subheader("📍 Analisis Berdasarkan Wilayah")
        
        if 'Kecamatan' in df_clean.columns and 'Prediksi_Status_Label' in df_clean.columns:
            wilayah_stats = df_clean.groupby('Kecamatan')['Prediksi_Status'].agg(['count', 'sum'])
            wilayah_stats.columns = ['Total', 'Sudah_Dapat']
            wilayah_stats['Belum_Dapat'] = wilayah_stats['Total'] - wilayah_stats['Sudah_Dapat']
            wilayah_stats['Persentase_Belum'] = (wilayah_stats['Belum_Dapat'] / wilayah_stats['Total'] * 100).round(1)
            
            st.dataframe(wilayah_stats.sort_values('Persentase_Belum', ascending=False), use_container_width=True)
        
        # Tampilkan yang diprediksi belum dapat bantuan
        st.subheader("🏠 Keluarga yang Diprediksi BELUM Menerima Bantuan")
        df_belum = df_clean[df_clean['Prediksi_Status'] == 0]
        
        if len(df_belum) > 0:
            # Pilih kolom yang relevan untuk ditampilkan
            display_cols = ['No', 'Nama', 'NIK', 'Klaster', 'Usulan', 
                          'Kabupaten/Kota', 'Kecamatan', 'Desa/Kelurahan', 
                          'Alamat Detail', 'Prediksi_Status_Label']
            
            # Filter hanya kolom yang ada
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
        
        # Visualisasi
        st.subheader("📈 Visualisasi Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribusi prediksi per klaster
            st.markdown("**Distribusi per Klaster**")
            if 'Klaster' in df_clean.columns:
                klaster_chart = df_clean.groupby(['Klaster', 'Prediksi_Status_Label']).size().unstack(fill_value=0)
                st.bar_chart(klaster_chart)
        
        with col2:
            # Distribusi per kecamatan
            st.markdown("**Distribusi per Kecamatan**")
            if 'Kecamatan' in df_clean.columns:
                kecamatan_chart = df_clean.groupby(['Kecamatan', 'Prediksi_Status_Label']).size().unstack(fill_value=0)
                # Ambil top 5 kecamatan
                top_kecamatan = kecamatan_chart.sum(axis=1).nlargest(5).index
                st.bar_chart(kecamatan_chart.loc[top_kecamatan])
        
        # Feature importance
        st.subheader("🔝 Tingkat Kepentingan Fitur")
        feature_names = X.columns
        importances = model.feature_importances_
        importance_df = pd.DataFrame({
            'Fitur': feature_names,
            'Importance': importances
        }).sort_values('Importance', ascending=False)
        
        # Tampilkan dengan chart
        st.bar_chart(importance_df.set_index('Fitur'))
        st.dataframe(importance_df, use_container_width=True)
        
        # Rekomendasi berdasarkan model
        st.subheader("💡 Rekomendasi Prioritas")
        
        if len(df_belum) > 0:
            # Urutkan berdasarkan probabilitas (gunakan predict_proba)
            try:
                probabilities = model.predict_proba(X)[:, 0]  # Probabilitas kelas 0 (belum)
                df_clean['Probabilitas_Belum'] = probabilities
                df_belum_with_prob = df_clean[df_clean['Prediksi_Status'] == 0].copy()
                
                # Urutkan berdasarkan probabilitas tertinggi (paling mungkin belum dapat)
                df_prioritas = df_belum_with_prob.sort_values('Probabilitas_Belum', ascending=False).head(10)
                
                st.markdown("**Top 10 Prioritas Berdasarkan Model:**")
                priority_cols = ['Nama', 'Klaster', 'Kecamatan', 'Desa/Kelurahan', 'Probabilitas_Belum']
                priority_cols = [col for col in priority_cols if col in df_prioritas.columns]
                st.dataframe(df_prioritas[priority_cols], use_container_width=True)
            except:
                st.info("Tidak dapat menghitung probabilitas untuk rekomendasi prioritas.")
        
        # Catatan penting
        st.info("""
        **⚠️ Catatan Penting:**
        1. Data target (sudah/belum dapat bantuan) dibuat **secara simulasi** untuk demonstrasi.
        2. **Alamat telah dipartisi** menjadi: Kabupaten, Kecamatan, Desa, Alamat Detail.
        3. Model mempertimbangkan **faktor wilayah** dalam prediksi.
        4. Untuk implementasi nyata, diperlukan data riil status penerimaan bantuan.
        5. Hasil prediksi adalah **rekomendasi**, bukan keputusan final.
        """)
        
    except Exception as e:
        st.error(f"❌ Terjadi kesalahan: {str(e)}")
        st.write("Pastikan file Excel memiliki format yang sesuai.")
        st.write("Detail error:", str(e))

else:
    # Tampilkan panduan jika belum upload file
    st.markdown("""
    ### 📋 Panduan Penggunaan:
    
    1. **Siapkan file Excel** dengan format seperti contoh di bawah.
    2. **Upload file** melalui menu di atas.
    3. **Model akan dilatih** secara otomatis.
    4. **Lihat hasil prediksi** keluarga yang belum menerima bantuan.
    
    ### 🗂️ Format Excel yang Disarankan:
    
    | No | Nama | NIK | No KK | Kabupaten/Kota | Kecamatan | Desa/Kelurahan | Alamat (Jalan/RT dan RW) | Klaster | Usulan |
    |----|------|-----|-------|----------------|-----------|----------------|--------------------------|---------|--------|
    | 1  | Hairiah | ... | ... | ... | ... | ... | ... | ... | ... |
    
    ### 🔧 Teknologi yang Digunakan:
    - **Python** dengan **scikit-learn** (Random Forest)
    - **Streamlit** untuk antarmuka web
    - **Pandas** untuk pengolahan data
    """)
    
    # Contoh data dengan struktur alamat terpisah
    example_data = {
        'No': [1, 2, 3],
        'Nama': ['Hairiah', 'Rahmat Al Khoirul', 'Diyon'],
        'NIK': ['32160***********', '32160***********', '32122***********'],
        'No KK': ['32160***********', '32160***********', '32122***********'],
        'Kabupaten/Kota': ['Kab. Bekasi', 'Kota Bekasi', 'Kota Bekasi'],
        'Kecamatan': ['Tambun Selatan', 'Tambun Selatan', 'Cibitung'],
        'Desa/Kelurahan': ['Sumber Jaya', 'Sumber Jaya', 'Wanasari'],
        'Alamat (Jalan/RT dan RW)': ['Kp. Pulo Rt 001 Rw 035', 'Kp. Pulo Rt 001 Rw 036', 'Bekasi Regensi I Rt 004 Rw 005'],
        'Klaster': ['Lansia', 'Anak', 'Anak'],
        'Usulan': ['Kebutuhan Lansia', 'ATK, Kebutuhan Pendidikan', 'ATK, Kebutuhan Pendidikan']
    }
    
    st.dataframe(pd.DataFrame(example_data), use_container_width=True)