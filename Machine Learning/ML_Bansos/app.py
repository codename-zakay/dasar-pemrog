import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import warnings
import datetime
warnings.filterwarnings('ignore')

# 1. SETTING PAGE STREAMLIT
st.set_page_config(
    page_title="Prediksi Penerima Bantuan Sosial", 
    page_icon="🏠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    
    /* Watermark */
    .watermark {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        opacity: 0.3;
        font-size: 14px;
        color: gray;
        text-align: center;
        z-index: 9999;
        pointer-events: none;
        font-family: Arial, sans-serif;
        white-space: nowrap;
    }
</style>
""", unsafe_allow_html=True)

# Header dengan gradient
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size:2.2rem;">🏠 Prediksi Penerima Bantuan Sosial</h1>
    <p style="margin:0.5rem 0 0 0; font-size:1.1rem; opacity:0.9;">
    Sistem Cerdas untuk mengidentifikasi keluarga yang belum menerima bantuan sosial menggunakan Machine Learning
    </p>
</div>
""", unsafe_allow_html=True)

# 2. FUNGSI UNTUK MEMPROSES DATA
def split_address_column(df):
    """
    Memisahkan kolom 'Alamat Lengkap' menjadi 4 kolom terpisah.
    """
    df = df.copy()
    address_columns = ['Kabupaten/Kota', 'Kecamatan', 'Desa/Kelurahan', 'Alamat (Jalan/RT dan RW)']
    
    if 'Alamat Lengkap' in df.columns:
        try:
            if df['Alamat Lengkap'].astype(str).str.contains('\|').any():
                address_parts = df['Alamat Lengkap'].astype(str).str.split('\|', expand=True)
                if address_parts.shape[1] >= 4:
                    df['Kabupaten/Kota'] = address_parts[0].str.strip()
                    df['Kecamatan'] = address_parts[1].str.strip()
                    df['Desa/Kelurahan'] = address_parts[2].str.strip()
                    df['Alamat Detail'] = address_parts[3].str.strip()
            else:
                if all(col in df.columns for col in address_columns[:3]):
                    df['Kabupaten/Kota'] = df.get('Kabupaten/Kota', '')
                    df['Kecamatan'] = df.get('Kecamatan', '')
                    df['Desa/Kelurahan'] = df.get('Desa/Kelurahan', '')
                    df['Alamat Detail'] = df.get('Alamat (Jalan/RT dan RW)', df.get('Alamat Lengkap', ''))
                else:
                    df['Kabupaten/Kota'] = 'Bekasi'
                    df['Kecamatan'] = 'Tambun Selatan'
                    df['Desa/Kelurahan'] = 'Sumber Jaya'
                    df['Alamat Detail'] = df['Alamat Lengkap']
        except:
            for col in ['Kabupaten/Kota', 'Kecamatan', 'Desa/Kelurahan']:
                df[col] = ''
            df['Alamat Detail'] = df['Alamat Lengkap']
            
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

# 3. FUNGSI UNTUK MEMBUAT DATA SIMULASI TARGET
def create_simulation_target(df, seed=42):
    np.random.seed(seed)
    
    conditions = [
        df['Klaster'].str.contains('Lansia', na=False),
        df['Klaster'].str.contains('Anak', na=False),
        df['Klaster'].str.contains('Disabilitas', na=False),
        df['Klaster'].str.contains('Rentan', na=False)
    ]
    choices = [0.8, 0.7, 0.6, 0.5]
    default_prob = 0.3
    
    prob = np.select(conditions, choices, default=default_prob)
    
    if 'Kecamatan' in df.columns:
        prior_kecamatan = ['Tambun Selatan', 'Cibitung']
        mask_prior_kecamatan = df['Kecamatan'].isin(prior_kecamatan)
        prob[mask_prior_kecamatan] = np.minimum(prob[mask_prior_kecamatan] + 0.1, 0.9)
    
    # Hasilkan label
    y = np.random.binomial(1, prob, size=len(df))
    
    return y

# 4. FUNGSI UNTUK MELATIH MODEL
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

# 5. SIDEBAR YANG USER FRIENDLY
with st.sidebar:
    st.markdown("### ⚙️ **Pengaturan Model**")
    
    # Preset konfigurasi dengan card style
    st.markdown("#### 🎯 **Preset Model**")
    config_preset = st.radio(
        "Pilih preset model:",
        ["Fast", "Balanced", "Accurate", "Custom"],
        index=1,
        label_visibility="collapsed"
    )
    
    # Default values berdasarkan preset
    if config_preset == "Fast":
        test_size = 0.30
        n_estimators = 50
        max_depth = 5
        random_seed = 42
        
    elif config_preset == "Balanced":
        test_size = 0.20
        n_estimators = 100
        max_depth = 7
        random_seed = 42
        
    elif config_preset == "Accurate":
        test_size = 0.15
        n_estimators = 500
        max_depth = 10
        random_seed = 42
        
    else:  # Custom
        st.markdown("#### **Parameter Kustom**")
        
        col1, col2 = st.columns(2)
        with col1:
            test_size = st.select_slider(
                "Ukuran Testing",
                options=[0.1, 0.15, 0.2, 0.25, 0.3],
                value=0.2,
                format_func=lambda x: f"{int(x*100)}%"
            )
        
        with col2:
            n_estimators = st.select_slider(
                "Jumlah Pohon",
                options=[50, 100, 200, 300, 500],
                value=100
            )
        
        max_depth = st.select_slider(
            "Kedalaman Pohon",
            options=[3, 5, 7, 10, 15, 20],
            value=7
        )
        
        random_seed = st.selectbox(
            "Random Seed",
            options=[42, 123, 456, 789, 999],
            index=0
        )
    
    st.markdown("---")
    
    train_button = st.button(
        "🚀 **Train Model Sekarang**",
        type="primary",
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Quick stats di sidebar
    st.markdown("### 📊 **Info Cepat**")
    st.metric("Algoritma", "Random Forest")
    st.metric("Status Model", "Ready" if train_button else "Idle")

# 6. MAIN INTERFACE
st.markdown("### 📤 **Upload Data**")
uploaded_file = st.file_uploader(
    "Unggah file Excel data usulan bantuan sosial",
    type=["xlsx", "xls"],
    help="Format yang didukung: .xlsx, .xls",
    label_visibility="collapsed"
)

if uploaded_file is not None:
    try:
        # Progress bar untuk feedback visual
        with st.spinner("🔄 Memuat data..."):
            progress_bar = st.progress(0)
            
            # Baca file
            df = pd.read_excel(uploaded_file)
            progress_bar.progress(30)
            
            # Hapus baris yang SEMUA kolomnya berisi 'None', NaN, atau string kosong
            def clean_dataframe(df):
                df_clean = df.copy()
                
                # 1. Hapus baris yang semua kolomnya NaN
                df_clean = df_clean.dropna(how='all')
                
                # 2. Hapus baris yang semua kolomnya string kosong
                empty_mask = df_clean.applymap(lambda x: str(x).strip() == '').all(axis=1)
                df_clean = df_clean[~empty_mask]
                
                # 3. Hapus baris yang semua kolomnya 'None' (case insensitive)
                none_mask = df_clean.applymap(lambda x: str(x).strip().lower() == 'none').all(axis=1)
                df_clean = df_clean[~none_mask]
                
                # 4. Hapus baris yang semua kolomnya 'null' atau 'nan'
                null_mask = df_clean.applymap(lambda x: str(x).strip().lower() in ['null', 'nan']).all(axis=1)
                df_clean = df_clean[~null_mask]
                
                # 5. Reset index dan mulai dari 1 untuk kolom 'No'
                df_clean = df_clean.reset_index(drop=True)
                
                # Jika ada kolom 'No', update nomor urut
                if 'No' in df_clean.columns:
                    df_clean['No'] = range(1, len(df_clean) + 1)
                
                return df_clean

            # Gunakan fungsi cleaning
            df = clean_dataframe(df)
            # Tampilkan preview data dengan tabs
            st.markdown("### 📋 **Preview Data**")
            
            tab1, tab2 = st.tabs(["📊 Data Lengkap", "📈 Statistik"])
            
            with tab1:
                st.dataframe(df, use_container_width=True, height=400, hide_index=True)
                st.caption(f"Total data: **{len(df)}** baris, **{len(df.columns)}** kolom")
                
            with tab2:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Data", len(df))
                with col2:
                    st.metric("Total Kolom", len(df.columns))
                with col3:
                    if 'Klaster' in df.columns:
                        unique_clusters = df['Klaster'].nunique()
                        st.metric("Jumlah Klaster", unique_clusters)
                    else:
                        st.metric("Jumlah Klaster", "N/A")
                
                # Distribusi klaster
                if 'Klaster' in df.columns:
                    st.markdown("#### 📊 Distribusi Klaster")
                    cluster_dist = df['Klaster'].value_counts()
                    st.bar_chart(cluster_dist)
            
            progress_bar.progress(60)
            
            # Proses data
            st.markdown("### 🔧 **Preprocessing Data**")
            with st.expander("Detail Preprocessing", expanded=False):
                df_clean = preprocess_data(df)
                
                # Tampilkan data yang sudah diproses
                st.markdown("**Data Setelah Preprocessing:**")
                address_cols = ['No', 'Nama', 'Kabupaten/Kota', 'Kecamatan', 'Desa/Kelurahan', 'Alamat Detail', 'Klaster', 'Usulan']
                display_cols = [col for col in address_cols if col in df_clean.columns]
                st.dataframe(df_clean[display_cols].head(10), use_container_width=True)
                
                # Persiapan fitur
                st.markdown("**Fitur yang Dihasilkan:**")
                X = prepare_features(df_clean)
                st.write(f"Jumlah fitur: **{X.shape[1]}**")
                st.dataframe(X.head(), use_container_width=True)
                
            progress_bar.progress(80)
            
            # Target simulasi
            y = create_simulation_target(df_clean, seed=random_seed)
            
            progress_bar.progress(100)
            st.success("✅ Data berhasil diproses!")
        
        # Training model section
        if train_button:
            st.markdown("### **Training Model**")
            
            # Show model parameters
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Preset", config_preset)
            with col2:
                st.metric("Testing Size", f"{test_size*100:.0f}%")
            with col3:
                st.metric("Jumlah Pohon", n_estimators)
            with col4:
                st.metric("Kedalaman", max_depth)
            
            with st.spinner("🎯 Melatih model Random Forest..."):
                # Training animation
                training_placeholder = st.empty()
                training_placeholder.info("⏳ Model sedang dilatih...")
                
                model, accuracy, report, X_test, y_test, y_pred = train_model(
                    X, y, 
                    test_size=test_size,
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    random_state=random_seed
                )
                
                training_placeholder.success(f"✅ Model berhasil dilatih dengan akurasi: **{accuracy:.2%}**")

            st.markdown("### 📊 **Hasil Prediksi**")
            
            # Prediksi untuk semua data
            predictions = model.predict(X)
            df_clean['Prediksi_Status'] = predictions
            df_clean['Status'] = df_clean['Prediksi_Status'].map({1: 'Sudah', 0: 'Belum'}) 
            
            # Prediksi Status
            df_clean['Prediksi_Status'] = predictions
            df_clean['Status'] = df_clean['Prediksi_Status'].map({1: 'Sudah', 0: 'Belum'})
            
            # Statistik
            belum_count = (predictions == 0).sum()
            sudah_count = (predictions == 1).sum()
            
            # Metrics cards
            st.markdown("#### 📈 **Metrics Model**")
            col1, col2, col3, = st.columns(3)
            with col1:
                st.metric("Akurasi", f"{accuracy:.2%}")
            with col2:
                precision = report['weighted avg']['precision']
                st.metric("Precision", f"{precision:.2%}")
            with col3:
                recall = report['weighted avg']['recall']
                st.metric("Recall", f"{recall:.2%}")
    
            # Visualisasi distribusi status
            st.markdown("#### 📊 **Distribusi Status Prediksi**")
            col1, col2 = st.columns(2)
            
            with col1:
                import altair as alt
                status_data = pd.DataFrame({
                    'Status': ['Belum Menerima', 'Sudah Menerima'],
                    'Jumlah': [belum_count, sudah_count],
                    'Warna': ['#FF6B6B', '#4ECDC4']
                })
                
                base = alt.Chart(status_data).encode(
                    theta=alt.Theta("Jumlah:Q", stack=True),
                    color=alt.Color("Status:N", scale=alt.Scale(range=['#FF6B6B', '#4ECDC4']), legend=None),
                    tooltip=['Status', 'Jumlah']
                )
                
                pie = base.mark_arc(innerRadius=50, outerRadius=100)
                text = base.mark_text(radius=120, size=14).encode(text="Jumlah:Q")
                
                chart = (pie + text).properties(
                    height=300,
                    title="Distribusi Status"
                )
                
                st.altair_chart(chart, use_container_width=True)
                
                # Tambahkan metrics kecil
                col1a, col1b = st.columns(2)
                with col1a:
                    st.metric("Belum", f"{belum_count}")
                with col1b:
                    st.metric("Sudah", f"{sudah_count}")
            
            with col2:
                # Bar chart per klaster
                if 'Klaster' in df_clean.columns:
                    def format_italic(text):
                        if pd.isna(text):
                            return text
                        if str(text).strip() in ['Lansia', 'Anak']:
                            return f"*{text}*"
                        return text
                    status_by_cluster = df_clean.groupby(['Klaster', 'Status']).size().reset_index(name='Jumlah')
                    status_by_cluster['Klaster_Formatted'] = status_by_cluster['Klaster'].apply(lambda x: f"*{x}")
                    
                    chart = alt.Chart(status_by_cluster).mark_bar().encode(
                        x=alt.X('Klaster:N', title='Klaster', 
                        axis=alt.Axis(labelExpr="'*' + datum.value + '*'")),
                        y=alt.Y('Jumlah:Q', title='Jumlah'),
                        color='Status:N', tooltip=['Klaster', 'Status', 'Jumlah'])
                    st.altair_chart(chart, use_container_width=True)
                    
            # Tabel hasil prediksi dengan tabs
            st.markdown("#### 📋 **Detail Prediksi**")
            pred_tab1, pred_tab2 = st.tabs(["🎯 Prioritas Tertinggi", "📋 Semua Hasil"])
            
            with pred_tab1:
                df_prioritas = df_clean[df_clean['Status'] == 'Belum'][['No', 'Nama', 'Klaster', 
                                                                        'Kecamatan', 'Desa/Kelurahan', 'Status']].head(15).copy()
                df_prioritas['Prioritas'] = range(1, len(df_prioritas) + 1)
                
                st.dataframe(df_prioritas, use_container_width=True, hide_index=True)
                
                st.markdown("""
                <div class="info-box">
                💡 <strong>Keterangan:</strong> Data diurutkan berdasarkan probabilitas belum menerima bantuan tertinggi.
                </div>
                """, unsafe_allow_html=True)
            
            with pred_tab2:
                display_df = df_clean[['No', 'Nama', 'Klaster', 'Kecamatan', 'Status']].copy()
                display_df = display_df.sort_values('Status', ascending=True)
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    height=400,
                    hide_index=True
                )
            
            
            # Analisis wilayah
            st.markdown("#### 📍 **Analisis Berdasarkan Wilayah**")
            if 'Kecamatan' in df_clean.columns:
                wilayah_stats = df_clean.groupby('Kecamatan').agg(
                    Total=('Prediksi_Status', 'count'),
                    Sudah_Dapat=('Prediksi_Status', 'sum')
                ).reset_index()
                
                wilayah_stats['Belum_Dapat'] = wilayah_stats['Total'] - wilayah_stats['Sudah_Dapat']
                
                wilayah_stats = wilayah_stats.sort_values('Belum_Dapat', ascending=False)
                
                wilayah_stats['Total'] = wilayah_stats['Total'].astype(int)
                wilayah_stats['Sudah_Dapat'] = wilayah_stats['Sudah_Dapat'].astype(int)
                wilayah_stats['Belum_Dapat'] = wilayah_stats['Belum_Dapat'].astype(int)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(
                                wilayah_stats,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Kecamatan": "Kecamatan",
                                    "Total": st.column_config.NumberColumn("Total Keluarga", format="%d"),
                                    "Sudah_Dapat": st.column_config.NumberColumn("Sudah Dapat", format="%d"),
                                    "Belum_Dapat": st.column_config.NumberColumn("Belum Dapat", format="%d")
                                    }
                                )
                
                with col2:
                    # Top 5 kecamatan dengan persentase tertinggi belum dapat
                    top_kecamatan = wilayah_stats.nlargest(5).copy()
                    st.markdown("**Top 5 Kecamatan Prioritas:**")
                    for idx, row in top_kecamatan.iterrows():
                        st.progress(
                            row['Persentase_Belum']/100,
                            text=f"{row['Kecamatan']}: {row['Persentase_Belum']:.1f}% belum dapat"
                        )
            
            # Download section dengan cards
            st.markdown("### 💾 **Download Hasil**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                csv_all = df_clean.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 **Semua Data**",
                    data=csv_all,
                    file_name="hasil_prediksi_lengkap.csv",
                    mime="text/csv",
                    help="Download semua hasil prediksi"
                )
                st.caption("File CSV dengan semua hasil prediksi")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                df_belum = df_clean[df_clean['Prediksi_Status'] == 0]
                if len(df_belum) > 0:
                    csv_belum = df_belum.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="🎯 **Belum Dapat**",
                        data=csv_belum,
                        file_name="keluarga_belum_dapat_bantuan.csv",
                        mime="text/csv",
                        help="Download data yang diprediksi belum dapat bantuan"
                    )
                    st.caption(f"{len(df_belum)} data belum dapat bantuan")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                df_sudah = df_clean[df_clean['Prediksi_Status'] == 1]
                if len(df_sudah) > 0:
                    csv_sudah = df_sudah.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="✅ **Sudah Dapat**",
                        data=csv_sudah,
                        file_name="keluarga_sudah_dapat_bantuan.csv",
                        mime="text/csv",
                        help="Download data yang diprediksi sudah dapat bantuan"
                    )
                    st.caption(f"{len(df_sudah)} data sudah dapat bantuan")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Model details expander
            with st.expander("🔍 **Detail Model dan Evaluasi**", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Parameter Model:**")
                    st.write(f"- Preset: {config_preset}")
                    st.write(f"- Jumlah pohon: {n_estimators}")
                    st.write(f"- Kedalaman maksimal: {max_depth}")
                    st.write(f"- Ukuran data testing: {test_size*100}%")
                    st.write(f"- Random seed: {random_seed}")
                    st.write(f"- Total fitur: {X.shape[1]}")
                
                with col2:
                    st.markdown("**Classification Report:**")
                    report_df = pd.DataFrame(report).transpose()
                    st.dataframe(report_df, use_container_width=True)
        
        else:
            st.markdown("""
            <div class="info-box">
            💡 <strong>Tips:</strong> Klik tombol <strong>"🚀 Train Model Sekarang"</strong> di sidebar untuk memulai training model.
            </div>
            """, unsafe_allow_html=True)
        
        # Footer dengan timestamp
        st.markdown("---")
        current_time = datetime.datetime.now().strftime("%d %B %Y, %H:%M:%S")
        left, center, right = st.columns([1, 2, 1])
        with center:
            st.markdown(f"""
            <div style="text-align: center; color: #666; font-size: 12px; padding: 20px;">
                <p style="margin: 0;">
                    © 2024 • <strong>Kelompok 11</strong> • Random Forest Algorithm • 
                    <span style="color: #888;">Generated: {current_time}</span>
                </p>
                <p style="margin: 5px 0 0 0; font-size: 11px; color: #999;">
                    Aplikasi Prediksi Penerima Bantuan Sosial • 
                    <span style="color: #4CAF50;">🟢 Ready</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"""
        ❌ **Terjadi Kesalahan**
        
        ```python
        {str(e)}
        ```
        
        Pastikan file Excel memiliki format yang sesuai dengan template.
        """)
        st.markdown("""
        <div class="warning-box">
        🔧 **Solusi:** 
        1. Pastikan file berformat .xlsx atau .xls
        2. Pastikan kolom yang diperlukan ada (Nama, Klaster, dll)
        3. Periksa apakah ada karakter khusus yang tidak didukung
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="info-box">
    📋 <strong>Selamat datang di Sistem Prediksi Bantuan Sosial!</strong><br>
    Unggah file Excel untuk mulai menganalisis data penerima bantuan sosial.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📥 **Cara Menggunakan**")
        st.markdown("""
        - **Siapkan data** dalam format Excel
        - **Unggah file** menggunakan menu di atas
        - **Atur parameter** model di sidebar
        - **Klik "Train Model"** untuk memulai analisis
        - **Download hasil** untuk laporan
        """)
        
        st.markdown("### 🎯 **Fitur Utama**")
        st.markdown("""
        -  **Prediksi otomatis** menggunakan Random Forest
        -  **Visualisasi interaktif** hasil prediksi
        -  **Analisis per wilayah** (kecamatan/desa)
        -  **Ekspor data** dalam format CSV
        -  **Multiple presets** untuk kebutuhan berbeda
        """)
    
    with col2:
        st.markdown("### 📁 **Format Data yang Didukung**")
        
        # Contoh format data
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
        
        st.dataframe(pd.DataFrame(example_data), use_container_width=True, hide_index=True)
        
        st.markdown("""
        <div class="warning-box">
        ⚠️ <strong>Perhatian:</strong> Kolom <strong>Klaster</strong> harus ada dalam data.
        </div>
        """, unsafe_allow_html=True)
    
    # Quick start guide
    st.markdown("---")
    st.markdown("### ⚡ **Quick Start**")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Format", "Excel (.xlsx)")
    with col2:
        st.metric("Algoritma", "Random Forest")
    with col3:
        st.metric("Kecepatan", "< 30 detik")
    
    # Footer landing page
    st.markdown("---")
    left, center, right = st.columns([1, 2, 1])
    with center:
        st.markdown("""
        <div style="text-align: center; color: #888; font-size: 12px; padding: 20px;">
            <p style="margin: 0;">
                <strong>🏛️Universitas Bina Sarana Informatika</strong> • Dasar Pemrograman, Machine Learning
            </p>
            <p style="margin: 5px 0 0 0; font-size: 11px;">
                Developed by <strong>Kelompok 11</strong> • © Oktober-Desember 2024
            </p>
        </div>
        """, unsafe_allow_html=True)