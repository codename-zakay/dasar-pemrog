"""
Frontend Streamlit untuk Machine Learning Klasifikasi
Aplikasi web untuk upload Excel, train model, dan prediksi
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi halaman
st.set_page_config(
    page_title="ML Klasifikasi dengan Excel",
    page_icon="🤖",
    layout="wide"
)

# CSS untuk styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🤖 Machine Learning Klasifikasi</h1>',
            unsafe_allow_html=True)
st.markdown("---")

# Sidebar untuk navigasi
st.sidebar.title("📋 Menu")
page = st.sidebar.radio(
    "Pilih Halaman:",
    ["📤 Upload & Train", "🔮 Prediksi", "📊 Info Model"]
)

# Session state untuk menyimpan model dan data
if 'model' not in st.session_state:
    st.session_state.model = None
if 'scaler' not in st.session_state:
    st.session_state.scaler = None
if 'label_encoders' not in st.session_state:
    st.session_state.label_encoders = {}
if 'feature_columns' not in st.session_state:
    st.session_state.feature_columns = None
if 'target_column' not in st.session_state:
    st.session_state.target_column = None
if 'df_original' not in st.session_state:
    st.session_state.df_original = None

# ============================================
# Halaman 1: Upload & Train
# ============================================
if page == "📤 Upload & Train":
    st.header("📤 Upload Dataset Excel & Training Model")

    # Upload file
    uploaded_file = st.file_uploader(
        "Pilih file Excel (.xlsx atau .xls)",
        type=['xlsx', 'xls'],
        help="Upload file Excel yang berisi dataset untuk training"
    )

    if uploaded_file is not None:
        try:
            # Baca Excel
            df = pd.read_excel(uploaded_file)
            st.session_state.df_original = df

            st.success(
                f"✅ File berhasil diupload! ({df.shape[0]} baris, {df.shape[1]} kolom)")

            # Tampilkan preview
            st.subheader("📋 Preview Dataset")
            st.dataframe(df.head(10), use_container_width=True)

            # Info dataset
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Jumlah Data", len(df))
            with col2:
                st.metric("Jumlah Fitur", len(df.columns) - 1)
            with col3:
                st.metric("Jumlah Kolom", len(df.columns))

            # Pilih kolom target
            st.subheader("⚙️ Konfigurasi Training")
            target_column = st.selectbox(
                "Pilih Kolom Target (yang akan diprediksi):",
                options=df.columns.tolist(),
                index=len(df.columns) - 1,
                help="Pilih kolom yang ingin diprediksi oleh model"
            )

            # Pilih model
            model_type = st.selectbox(
                "Pilih Algoritma Model:",
                options=['random_forest', 'svm',
                         'naive_bayes', 'decision_tree'],
                format_func=lambda x: {
                    'random_forest': '🌲 Random Forest',
                    'svm': '🔷 Support Vector Machine',
                    'naive_bayes': '📊 Naive Bayes',
                    'decision_tree': '🌳 Decision Tree'
                }[x],
                help="Pilih algoritma machine learning yang akan digunakan"
            )

            # Test size
            test_size = st.slider(
                "Proporsi Data Test:",
                min_value=0.1,
                max_value=0.5,
                value=0.2,
                step=0.05,
                help="Persentase data yang digunakan untuk testing"
            )

            # Tombol train
            if st.button("🚀 Train Model", type="primary", use_container_width=True):
                with st.spinner("Sedang memproses data dan training model..."):
                    try:
                        # Preprocessing
                        df_processed = df.copy()

                        # Handle missing values
                        for col in df_processed.columns:
                            if col != target_column:
                                if df_processed[col].dtype in ['int64', 'float64']:
                                    df_processed[col].fillna(
                                        df_processed[col].median(), inplace=True)
                                else:
                                    df_processed[col].fillna(df_processed[col].mode()[0] if len(
                                        df_processed[col].mode()) > 0 else '', inplace=True)

                        # Encode categorical
                        label_encoders = {}
                        feature_cols = []

                        for col in df_processed.select_dtypes(include=['object']).columns:
                            if col != target_column:
                                le = LabelEncoder()
                                df_processed[col + '_encoded'] = le.fit_transform(
                                    df_processed[col].astype(str))
                                label_encoders[col] = le
                                feature_cols.append(col + '_encoded')

                        # Tambahkan kolom numerik
                        for col in df_processed.columns:
                            if col != target_column and not col.endswith('_encoded'):
                                if df_processed[col].dtype in ['int64', 'float64']:
                                    feature_cols.append(col)

                        # Prepare X dan y
                        X = df_processed[feature_cols].values
                        y = df_processed[target_column].values

                        # Encode target jika kategorikal
                        if df[target_column].dtype == 'object':
                            le_target = LabelEncoder()
                            y = le_target.fit_transform(y)
                            label_encoders[target_column] = le_target

                        # Split data
                        X_train, X_test, y_train, y_test = train_test_split(
                            X, y, test_size=test_size, random_state=42
                        )

                        # Normalisasi
                        scaler = StandardScaler()
                        X_train_scaled = scaler.fit_transform(X_train)
                        X_test_scaled = scaler.transform(X_test)

                        # Train model
                        models = {
                            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
                            'svm': SVC(kernel='rbf', random_state=42),
                            'naive_bayes': GaussianNB(),
                            'decision_tree': DecisionTreeClassifier(random_state=42)
                        }

                        model = models[model_type]
                        model.fit(X_train_scaled, y_train)

                        # Evaluasi
                        y_pred = model.predict(X_test_scaled)
                        accuracy = accuracy_score(y_test, y_pred)

                        # Simpan ke session state
                        st.session_state.model = model
                        st.session_state.scaler = scaler
                        st.session_state.label_encoders = label_encoders
                        st.session_state.feature_columns = feature_cols
                        st.session_state.target_column = target_column

                        # Tampilkan hasil
                        st.success(f"✅ Model berhasil di-train!")

                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Akurasi Model",
                                      f"{accuracy:.4f} ({accuracy*100:.2f}%)")
                        with col2:
                            st.metric("Jumlah Fitur", len(feature_cols))

                        # Classification report
                        st.subheader("📊 Classification Report")
                        report = classification_report(
                            y_test, y_pred, output_dict=True)
                        st.dataframe(pd.DataFrame(
                            report).transpose(), use_container_width=True)

                        # Confusion matrix
                        st.subheader("📈 Confusion Matrix")
                        cm = confusion_matrix(y_test, y_pred)
                        fig, ax = plt.subplots(figsize=(8, 6))
                        sns.heatmap(cm, annot=True, fmt='d',
                                    cmap='Blues', ax=ax)
                        ax.set_xlabel('Predicted')
                        ax.set_ylabel('Actual')
                        ax.set_title('Confusion Matrix')
                        st.pyplot(fig)

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.exception(e)

        except Exception as e:
            st.error(f"❌ Error membaca file: {str(e)}")
            st.exception(e)

# ============================================
# Halaman 2: Prediksi
# ============================================
elif page == "🔮 Prediksi":
    st.header("🔮 Prediksi Data Baru")

    if st.session_state.model is None:
        st.warning(
            "⚠️ Model belum di-train! Silakan ke halaman 'Upload & Train' terlebih dahulu.")
    else:
        st.info(
            f"✅ Model siap digunakan. Target: **{st.session_state.target_column}**")

        # Input manual
        st.subheader("📝 Input Data untuk Prediksi")

        if st.session_state.df_original is not None:
            # Ambil contoh dari dataset
            example_row = st.session_state.df_original.iloc[0]

            # Buat form input
            input_data = {}
            cols = st.columns(3)

            for idx, col_name in enumerate(st.session_state.feature_columns):
                col_idx = idx % 3
                with cols[col_idx]:
                    # Cek apakah kolom ini encoded atau original
                    original_col = col_name.replace('_encoded', '')

                    if original_col in st.session_state.df_original.columns:
                        col_dtype = st.session_state.df_original[original_col].dtype

                        if col_dtype in ['int64', 'float64']:
                            input_data[col_name] = st.number_input(
                                f"{original_col}",
                                value=float(example_row[original_col]) if pd.notna(
                                    example_row[original_col]) else 0.0,
                                step=0.1
                            )
                        else:
                            # Untuk categorical, tampilkan selectbox
                            unique_vals = st.session_state.df_original[original_col].dropna(
                            ).unique()
                            selected_val = st.selectbox(
                                f"{original_col}", options=unique_vals)
                            # Encode value
                            if original_col in st.session_state.label_encoders:
                                input_data[col_name] = st.session_state.label_encoders[original_col].transform([
                                                                                                               selected_val])[0]
                            else:
                                input_data[col_name] = 0
                    else:
                        # Kolom numerik langsung
                        input_data[col_name] = st.number_input(
                            f"{col_name}",
                            value=0.0,
                            step=0.1
                        )

        if st.button("🔮 Prediksi", type="primary", use_container_width=True):
            try:
                # Siapkan data untuk prediksi
                X_new = np.array([[input_data[col]
                                 for col in st.session_state.feature_columns]])

                # Normalisasi
                X_new_scaled = st.session_state.scaler.transform(X_new)

                # Prediksi
                prediction = st.session_state.model.predict(X_new_scaled)[0]

                # Decode jika perlu
                if st.session_state.target_column in st.session_state.label_encoders:
                    prediction_decoded = st.session_state.label_encoders[st.session_state.target_column].inverse_transform([
                                                                                                                           prediction])[0]
                else:
                    prediction_decoded = prediction

                # Tampilkan hasil
                st.success(f"✅ Prediksi: **{prediction_decoded}**")

                # Probabilitas (jika ada)
                if hasattr(st.session_state.model, 'predict_proba'):
                    proba = st.session_state.model.predict_proba(X_new_scaled)[
                        0]
                    st.subheader("📊 Probabilitas Prediksi")
                    proba_df = pd.DataFrame({
                        'Kelas': [st.session_state.label_encoders[st.session_state.target_column].inverse_transform([i])[0]
                                  if st.session_state.target_column in st.session_state.label_encoders else i
                                  for i in range(len(proba))],
                        'Probabilitas': proba
                    })
                    st.bar_chart(proba_df.set_index('Kelas'))

            except Exception as e:
                st.error(f"❌ Error prediksi: {str(e)}")
                st.exception(e)

# ============================================
# Halaman 3: Info Model
# ============================================
elif page == "📊 Info Model":
    st.header("📊 Informasi Model")

    if st.session_state.model is None:
        st.warning("⚠️ Model belum di-train!")
    else:
        st.success("✅ Model sudah di-train dan siap digunakan")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Jenis Model", type(st.session_state.model).__name__)
        with col2:
            st.metric("Jumlah Fitur", len(st.session_state.feature_columns)
                      if st.session_state.feature_columns else 0)

        st.subheader("📋 Fitur yang Digunakan")
        if st.session_state.feature_columns:
            st.write(pd.DataFrame({
                'Fitur': st.session_state.feature_columns
            }))

        st.subheader("🎯 Kolom Target")
        st.write(f"**{st.session_state.target_column}**")

        # Feature importance (jika Random Forest)
        if hasattr(st.session_state.model, 'feature_importances_'):
            st.subheader("📊 Feature Importance")
            importance_df = pd.DataFrame({
                'Fitur': st.session_state.feature_columns,
                'Importance': st.session_state.model.feature_importances_
            }).sort_values('Importance', ascending=False)

            st.bar_chart(importance_df.set_index('Fitur'))
            st.dataframe(importance_df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>🤖 Machine Learning Klasifikasi dengan Streamlit</p>",
            unsafe_allow_html=True)
