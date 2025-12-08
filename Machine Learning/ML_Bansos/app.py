# app.py

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
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
    Memisahkan kolom 'Alamat Lengkap' menjadi 4 kolom terpisah.
    """
    df = df.copy()
    
    # Cek apakah kolom alamat sudah terpisah
    address_columns = ['Kabupaten/Kota', 'Kecamatan', 'Desa/Kelurahan', 'Alamat (Jalan/RT dan RW)']
    
    if 'Alamat Lengkap' in df.columns:
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
                # Gunakan kolom yang sudah ada
                if all(col in df.columns for col in address_columns[:3]):
                    df['Kabupaten/Kota'] = df.get('Kabupaten/Kota', '')
                    df['Kecamatan'] = df.get('Kecamatan', '')
                    df['Desa/Kelurahan'] = df.get('Desa/Kelurahan', '')
                    df['Alamat Detail'] = df.get('Alamat (Jalan/RT dan RW)', df.get('Alamat Lengkap', ''))
                else:
                    # Buat kolom default
                    df['Kabupaten/Kota'] = 'Bekasi'
                    df['Kecamatan'] = 'Tambun Selatan'
                    df['Desa/Kelurahan'] = 'Sumber Jaya'
                    df['Alamat Detail'] = df['Alamat Lengkap']
        except:
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
    
    # Hapus baris kosong
    required_cols = ['Nama', 'Klaster']
    df.dropna(subset=required_cols, inplace=True)
    
    # Isi missing value
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
    
    # Fitur 1: Panjang alamat detail
    df_features['Panjang_Alamat_Detail'] = df_features['Alamat Detail'].apply(lambda x: len(str(x).split()))
    
    # Fitur 2: Panjang NIK
    df_features['Panjang_NIK'] = df_features['NIK'].apply(lambda x: len(str(x)))
    
    # Fitur 3: Encoding Klaster
    le_klaster = LabelEncoder()
    df_features['Klaster_Encoded'] = le_klaster.fit_transform(df_features['Klaster'])
    
    # Fitur 4: Apakah ada nomor KK?
    df_features['Ada_KK'] = df_features['No KK'].apply(lambda x: 1 if pd.notna(x) and str(x).strip() != '' else 0)
    
    # Fitur 5-7: Encoding wilayah
    le_kabupaten = LabelEncoder()
    df_features['Kabupaten_Encoded'] = le_kabupaten.fit_transform(df_features['Kabupaten/Kota'].fillna('Tidak Diketahui'))
    
    le_kecamatan = LabelEncoder()
    df_features['Kecamatan_Encoded'] = le_kecamatan.fit_transform(df_features['Kecamatan'].fillna('Tidak Diketahui'))
    
    le_desa = LabelEncoder()
    df_features['Desa_Encoded'] = le_desa.fit_transform(df_features['Desa/Kelurahan'].fillna('Tidak Diketahui'))
    
    # Fitur 8: Ada RT/RW
    df_features['Ada_RT_RW'] = df_features['Alamat Detail'].apply(
        lambda x: 1 if any(keyword in str(x).lower() for keyword in ['rt', 'rw']) else 0
    )
    
    # Fitur 9: Panjang nama
    df_features['Panjang_Nama'] = df_features['Nama'].apply(lambda x: len(str(x).split()))
    
    # Pilih fitur
    feature_cols = [
        'Panjang_Alamat_Detail', 'Panjang_NIK', 'Klaster_Encoded', 'Ada_KK',
        'Kabupaten_Encoded', 'Kecamatan_Encoded', 'Desa_Encoded',
        'Ada_RT_RW', 'Panjang_Nama'
    ]
    
    return df_features[feature_cols]

# ============================
# 3. FUNGSI UNTUK MEMBUAT DATA SIMULASI TARGET
# ============================
def create_simulation_target(df, seed=42):
    """
    Membuat target simulasi untuk training model.
    """
    np.random.seed(seed)
    
    # Beri bobot berdasarkan klaster
    conditions = [
        df['Klaster'].str.contains('Lansia', na=False),
        df['Klaster'].str.contains('Anak', na=False),
        df['Klaster'].str.contains('Disabilitas', na=False),
        df['Klaster'].str.contains('Rentan', na=False)
    ]
    choices = [0.8, 0.7, 0.6, 0.5]
    default_prob = 0.3
    
    prob = np.select(conditions, choices, default=default_prob)
    
    # Tambah bobot berdasarkan kecamatan
    if 'Kecamatan' in df.columns:
        prior_kecamatan = ['Tambun Selatan', 'Cibitung']
        mask_prior_kecamatan = df['Kecamatan'].isin(prior_kecamatan)
        prob[mask_prior_kecamatan] = np.minimum(prob[mask_prior_kecamatan] + 0.1, 0.9)
    
    # Hasilkan label
    y = np.random.binomial(1, prob, size=len(df))
    
    return y

# ============================
# 4. FUNGSI UNTUK MELATIH MODEL
# ============================
def train_model(X, y, test_size=0.2, n_estimators=100, max_depth=7, random_state=42):
    """
    Melatih model Random Forest dengan parameter yang bisa diatur.
    """
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Inisialisasi model
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
        class_weight='balanced',
        min_samples_split=5,
        min_samples_leaf=2
    )
    
    # Training
    model.fit(X_train, y_train)
    
    # Evaluasi
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    # Classification report
    report = classification_report(y_test, y_pred, output_dict=True)
    
    return model, acc, report, X_test, y_test, y_pred

# ============================
# 5. INTERFACE STREAMLIT
# ============================

# Upload file
uploaded_file = st.file_uploader("📂 Upload file Excel data usulan bantuan", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Baca file
        df = pd.read_excel(uploaded_file)
        
        # Tampilkan semua data dalam container scrollable
        st.subheader("📊 Data Lengkap Usulan Bantuan")
        
        # Container untuk tabel dengan tinggi tetap dan scroll
        container = st.container(height=400)  # Tinggi 400px, bisa di-scroll
        with container:
            st.dataframe(df, use_container_width=True)
        
        st.caption(f"Total data: {len(df)} baris, {len(df.columns)} kolom")
        
        # Sidebar untuk pengaturan model
        st.sidebar.header("⚙️ Pengaturan Model")
        
        # Parameter model
        test_size = st.sidebar.slider("Ukuran Data Testing (%)", 10, 40, 20) / 100
        n_estimators = st.sidebar.slider("Jumlah Pohon (n_estimators)", 50, 500, 100, 50)
        max_depth = st.sidebar.slider("Kedalaman Maksimal (max_depth)", 3, 20, 7)
        random_seed = st.sidebar.number_input("Random Seed", 1, 100, 42)
        
        # Tombol untuk training manual
        train_button = st.sidebar.button("🚀 Train Model Sekarang", type="primary")
        
        # Proses data
        with st.spinner("🔄 Memproses data..."):
            df_clean = preprocess_data(df)
            
            # Tampilkan data yang sudah diproses
            st.subheader("🏠 Data Setelah Preprocessing")
            
            # Container untuk tabel data yang diproses
            container_proses = st.container(height=300)
            with container_proses:
                address_cols = ['No', 'Nama', 'Kabupaten/Kota', 'Kecamatan', 'Desa/Kelurahan', 'Alamat Detail', 'Klaster', 'Usulan']
                display_cols = [col for col in address_cols if col in df_clean.columns]
                st.dataframe(df_clean[display_cols].head(20), use_container_width=True)
            
            # Persiapan fitur dan target
            X = prepare_features(df_clean)
            y = create_simulation_target(df_clean, seed=random_seed)
            
        # Training model (otomatis atau manual)
        if train_button or not train_button:
            with st.spinner("🤖 Melatih model Random Forest..."):
                model, accuracy, report, X_test, y_test, y_pred = train_model(
                    X, y, 
                    test_size=test_size,
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    random_state=random_seed
                )
            
            st.success(f"✅ Model berhasil dilatih!")
            
            # Tampilkan metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Akurasi", f"{accuracy:.2%}")
            with col2:
                precision = report['weighted avg']['precision']
                st.metric("Precision", f"{precision:.2%}")
            with col3:
                recall = report['weighted avg']['recall']
                st.metric("Recall", f"{recall:.2%}")
            with col4:
                f1 = report['weighted avg']['f1-score']
                st.metric("F1-Score", f"{f1:.2%}")
            
            # Prediksi untuk semua data
            predictions = model.predict(X)
            df_clean['Prediksi_Status'] = predictions
            df_clean['Status'] = df_clean['Prediksi_Status'].map({1: 'Sudah', 0: 'Belum'})
            
            # Hitung probabilitas
            probabilities = model.predict_proba(X)[:, 0]
            df_clean['Probabilitas_Belum'] = probabilities
            
            # Statistik
            belum_count = (predictions == 0).sum()
            sudah_count = (predictions == 1).sum()
            
            # Tampilkan hasil prediksi
            st.subheader("📋 Hasil Prediksi Semua Data")
            
            # Container untuk hasil prediksi
            container_prediksi = st.container(height=400)
            with container_prediksi:
                result_cols = ['No', 'Nama', 'Klaster', 'Kecamatan', 'Desa/Kelurahan', 
                             'Status', 'Probabilitas_Belum']
                result_cols = [col for col in result_cols if col in df_clean.columns]
                
                # Urutkan berdasarkan probabilitas belum
                df_display = df_clean[result_cols].sort_values('Probabilitas_Belum', ascending=False)
                st.dataframe(df_display, use_container_width=True)
            
            # Analisis berdasarkan wilayah
            st.subheader("📍 Analisis Berdasarkan Wilayah")
            
            if 'Kecamatan' in df_clean.columns and 'Status' in df_clean.columns:
                wilayah_stats = df_clean.groupby('Kecamatan').agg(
                    Total=('Prediksi_Status', 'count'),
                    Sudah_Dapat=('Prediksi_Status', 'sum'),
                    Rata_Rata_Probabilitas=('Probabilitas_Belum', 'mean')
                ).reset_index()
                
                wilayah_stats['Belum_Dapat'] = wilayah_stats['Total'] - wilayah_stats['Sudah_Dapat']
                wilayah_stats['Persentase_Belum'] = (wilayah_stats['Belum_Dapat'] / wilayah_stats['Total'] * 100)
                wilayah_stats['Persentase_Belum_Display'] = wilayah_stats['Persentase_Belum'].apply(lambda x: f"{x:.1f}%")
                
                # Format kolom
                wilayah_stats['Sudah_Dapat'] = wilayah_stats['Sudah_Dapat'].astype(int)
                wilayah_stats['Belum_Dapat'] = wilayah_stats['Belum_Dapat'].astype(int)
                wilayah_stats['Rata_Rata_Probabilitas'] = wilayah_stats['Rata_Rata_Probabilitas'].apply(lambda x: f"{x:.2%}")
                
                # Tampilkan tabel
                display_cols = ['Kecamatan', 'Total', 'Sudah_Dapat', 'Belum_Dapat', 
                              'Persentase_Belum_Display', 'Rata_Rata_Probabilitas']
                
                # Urutkan berdasarkan persentase belum
                wilayah_stats_sorted = wilayah_stats.sort_values('Persentase_Belum', ascending=False)
                
                st.dataframe(wilayah_stats_sorted[display_cols], use_container_width=True)
            
            # Visualisasi Data
            st.subheader("📊 Visualisasi Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Status Bantuan Sosial - Klaster**")
                if 'Klaster' in df_clean.columns:
                    klaster_chart = df_clean.groupby(['Klaster', 'Status']).size().unstack(fill_value=0)
                    
                    # Transpose untuk label horizontal
                    klaster_chart_t = klaster_chart.T
                    st.bar_chart(klaster_chart_t)
            
            with col2:
                st.markdown("**Status Bantuan Sosial - Kecamatan**")
                if 'Kecamatan' in df_clean.columns:
                    kecamatan_data = df_clean['Kecamatan'].value_counts().head(5)
                    
                    # Buat DataFrame untuk chart horizontal
                    kecamatan_df = pd.DataFrame({
                        'Kecamatan': kecamatan_data.index,
                        'Jumlah': kecamatan_data.values
                    })
                    
                    # Set index ke Kecamatan untuk chart horizontal
                    kecamatan_df.set_index('Kecamatan', inplace=True)
                    st.bar_chart(kecamatan_df)
            
            # Visualisasi tambahan
            st.markdown("**Total Keseluruhan Status Data**")
            col1, col2 = st.columns(2)
            
            with col1:
                status_counts = df_clean['Status'].value_counts()
                status_df = pd.DataFrame({
                    'Status': status_counts.index,
                    'Jumlah': status_counts.values
                })
                status_df.set_index('Status', inplace=True)
                st.bar_chart(status_df)
            
            with col2:
                # Pie chart untuk status
                if 'Status' in df_clean.columns:
                    import plotly.express as px
                    fig = px.pie(df_clean, names='Status', 
                                title='Proporsi Status Prediksi')
                    st.bar_chart(fig, use_container_width=True)
            
            # Feature Importance
            st.subheader("🔝 Tingkat Kepentingan Fitur")
            
            feature_names = X.columns
            importances = model.feature_importances_
            importance_df = pd.DataFrame({
                'Fitur': feature_names,
                'Importance': importances
            }).sort_values('Importance', ascending=False)
            
            # Bar chart horizontal untuk feature importance
            importance_df_sorted = importance_df.sort_values('Importance', ascending=True)
            importance_df_sorted.set_index('Fitur', inplace=True)
            
            st.bar_chart(importance_df_sorted)
            
            # Tabel feature importance
            importance_df['Importance_Pct'] = importance_df['Importance'].apply(lambda x: f"{x:.2%}")
            st.dataframe(importance_df[['Fitur', 'Importance_Pct']], use_container_width=True)
            
            # Rekomendasi Prioritas
            st.subheader("🎯 Rekomendasi Prioritas Penerima Bantuan")
            
            if 'Probabilitas_Belum' in df_clean.columns:
                # Ambil 10 dengan probabilitas tertinggi untuk belum dapat
                df_prioritas = df_clean.nlargest(10, 'Probabilitas_Belum')[['No', 'Nama', 'Klaster', 
                                                                           'Kecamatan', 'Desa/Kelurahan', 
                                                                           'Probabilitas_Belum']].copy()
                
                df_prioritas['Probabilitas_Belum'] = df_prioritas['Probabilitas_Belum'].apply(lambda x: f"{x:.2%}")
                
                st.dataframe(df_prioritas, use_container_width=True)
            
            # Download hasil
            st.subheader("💾 Download Hasil Analisis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Download hasil prediksi
                csv_all = df_clean.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Semua Hasil Prediksi (CSV)",
                    data=csv_all,
                    file_name="hasil_prediksi_lengkap.csv",
                    mime="text/csv",
                )
            
            with col2:
                # Download yang belum dapat
                df_belum = df_clean[df_clean['Prediksi_Status'] == 0]
                if len(df_belum) > 0:
                    csv_belum = df_belum.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Belum Dapat Bantuan (CSV)",
                        data=csv_belum,
                        file_name="keluarga_belum_dapat_bantuan.csv",
                        mime="text/csv",
                    )
            
            # Informasi model
            with st.expander("📊 Detail Model dan Evaluasi"):
                st.markdown("**Classification Report:**")
                st.json(report)
                
                st.markdown("**Parameter Model:**")
                st.write(f"- Jumlah pohon: {n_estimators}")
                st.write(f"- Kedalaman maksimal: {max_depth}")
                st.write(f"- Ukuran data testing: {test_size*100}%")
                st.write(f"- Random seed: {random_seed}")
        
        # Catatan penting
        st.info("""
        **ℹ️ Informasi Penting:**
        1. **Training Model**: Gunakan sidebar untuk mengatur parameter dan klik "Train Model Sekarang"
        2. **Data Target**: Dibuat secara simulasi untuk demonstrasi
        3. **Scrollable Tables**: Semua tabel dapat di-scroll untuk melihat data lengkap
        4. **Persentase**: Ditampilkan dengan format % pada analisis wilayah
        5. **Visualisasi**: Label ditampilkan secara horizontal untuk kemudahan membaca
        """)
        
    except Exception as e:
        st.error(f"❌ Terjadi kesalahan: {str(e)}")
        st.write("Pastikan file Excel memiliki format yang sesuai.")

else:
    # Tampilkan panduan
    st.markdown("""
    ## 📋 Panduan Penggunaan
    
    ### 1. **Persiapkan Data**
    Siapkan file Excel dengan format:
    
    | No | Nama | NIK | No KK  | Kabupaten/Kota | Kecamatan | Desa/Kelurahan | Alamat Detail | Klaster | Usulan |
    |----|------|-----|--------|----------------|-----------|----------------|---------------|---------|--------|   
    
    ### 2. **Upload Data**
    Gunakan menu upload di atas untuk mengirim file Excel.
    
    ### 3. **Atur Model (Opsional)**
    Gunakan sidebar untuk mengatur parameter model:
    - Ukuran data testing
    - Jumlah pohon keputusan
    - Kedalaman maksimal
    - Random seed
    
    ### ✨ Fitur Baru:
    - **Tabel Scrollable**: Semua data ditampilkan dalam tabel yang bisa di-scroll
    - **Training Manual**: Kontrol penuh atas parameter model
    - **Format Persen**: Persentase ditampilkan dengan simbol %
    - **Visualisasi Horizontal**: Label lebih mudah dibaca
    """)
    
    # Contoh data
    example_data = {
        'No': [1, 2, 3],
        'Nama': ['Hairiah', 'Rahmat Al Khoirul', 'Diyon'],
        'NIK': ['3216064304680020', '3216061201150013', '3212232911030003'],
        'No KK': ['3216061111100180', '3216060603230030', '3212230206099955'],
        'Kabupaten/Kota': ['Bekasi', 'Bekasi', 'Bekasi'],
        'Kecamatan': ['Tambun Selatan', 'Tambun Selatan', 'Cibitung'],
        'Desa/Kelurahan': ['Sumber Jaya', 'Sumber Jaya', 'Wanasari'],
        'Alamat Detail': ['Kp. Pulo Rt 001 Rw 035', 'Kp. Pulo Rt 001 Rw 036', 'Bekasi Regensi I Rt 004 Rw 005'],
        'Klaster': ['Lansia', 'Anak', 'Anak'],
        'Usulan': ['Kebutuhan Lansia', 'ATK, Kebutuhan Pendidikan', 'ATK, Kebutuhan Pendidikan']
    }
    
    st.dataframe(pd.DataFrame(example_data), use_container_width=True)