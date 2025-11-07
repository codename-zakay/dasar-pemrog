"""
Machine Learning Klasifikasi dengan Dataset Excel
Program untuk training model klasifikasi dari data Excel
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import os


class MLClassifier:
    """Class untuk handling machine learning klasifikasi"""

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = None
        self.target_column = None

    def load_excel(self, file_path, sheet_name=0, target_column=None):
        """
        Load dataset dari file Excel

        Parameters:
        - file_path: path ke file Excel
        - sheet_name: nama sheet atau index (default: 0)
        - target_column: nama kolom target (jika None, akan menggunakan kolom terakhir)
        """
        try:
            # Baca Excel
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(
                f"✅ Dataset berhasil dimuat: {df.shape[0]} baris, {df.shape[1]} kolom")

            # Tentukan target column
            if target_column is None:
                # Gunakan kolom terakhir sebagai default
                target_column = df.columns[-1]

            self.target_column = target_column

            # Tampilkan info dataset
            print(f"\n📊 Informasi Dataset:")
            print(f"   - Jumlah data: {len(df)}")
            print(f"   - Jumlah fitur: {len(df.columns) - 1}")
            print(f"   - Kolom target: {target_column}")
            print(f"\n📋 Preview Data:")
            print(df.head())
            print(f"\n📈 Info Dataset:")
            print(df.info())
            print(f"\n📊 Statistik Deskriptif:")
            print(df.describe())

            return df

        except Exception as e:
            print(f"❌ Error loading Excel: {str(e)}")
            raise

    def preprocess_data(self, df, target_column=None):
        """
        Preprocess data untuk training

        Parameters:
        - df: DataFrame
        - target_column: nama kolom target
        """
        if target_column is None:
            target_column = self.target_column

        # Copy dataframe
        df_processed = df.copy()

        # Handle missing values
        if df_processed.isnull().sum().sum() > 0:
            print(f"\n⚠️  Ditemukan missing values, mengisi dengan median/mode...")
            for col in df_processed.columns:
                if col != target_column:
                    if df_processed[col].dtype in ['int64', 'float64']:
                        df_processed[col].fillna(
                            df_processed[col].median(), inplace=True)
                    else:
                        df_processed[col].fillna(
                            df_processed[col].mode()[0], inplace=True)

        # Encode categorical variables
        self.label_encoders = {}
        for col in df_processed.select_dtypes(include=['object']).columns:
            if col != target_column:
                le = LabelEncoder()
                df_processed[col +
                             '_encoded'] = le.fit_transform(df_processed[col].astype(str))
                self.label_encoders[col] = le
                print(f"   ✅ Encoded: {col}")

        # Pilih features (semua kolom kecuali target dan kolom original yang sudah di-encode)
        feature_cols = []
        for col in df_processed.columns:
            if col != target_column and not col.endswith('_encoded'):
                if df_processed[col].dtype in ['int64', 'float64']:
                    feature_cols.append(col)

        # Tambahkan kolom yang sudah di-encode
        feature_cols.extend(
            [col for col in df_processed.columns if col.endswith('_encoded')])

        self.feature_columns = feature_cols

        # Prepare X dan y
        X = df_processed[feature_cols].values
        y = df_processed[target_column].values

        # Encode target jika kategorikal
        if df[target_column].dtype == 'object':
            le_target = LabelEncoder()
            y = le_target.fit_transform(y)
            self.label_encoders[target_column] = le_target
            print(f"   ✅ Encoded target: {target_column}")

        print(f"\n✅ Preprocessing selesai!")
        print(f"   - Features: {len(feature_cols)} kolom")
        print(f"   - Samples: {len(X)} data")
        print(f"   - Classes: {len(np.unique(y))} kelas")

        return X, y, df_processed

    def train_model(self, X, y, model_type='random_forest', test_size=0.2, random_state=42):
        """
        Train model klasifikasi

        Parameters:
        - X: features
        - y: target
        - model_type: jenis model ('random_forest', 'svm', 'naive_bayes', 'decision_tree')
        - test_size: proporsi data test
        - random_state: random seed
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        # Normalisasi
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Pilih model
        models = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=random_state),
            'svm': SVC(kernel='rbf', random_state=random_state),
            'naive_bayes': GaussianNB(),
            'decision_tree': DecisionTreeClassifier(random_state=random_state)
        }

        if model_type not in models:
            raise ValueError(
                f"Model type harus salah satu dari: {list(models.keys())}")

        self.model = models[model_type]

        print(f"\n🚀 Training model: {model_type}...")
        self.model.fit(X_train_scaled, y_train)

        # Evaluasi
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)

        print(f"\n✅ Training selesai!")
        print(f"   - Akurasi: {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"\n📊 Classification Report:")
        print(classification_report(y_test, y_pred))

        return {
            'accuracy': accuracy,
            'y_test': y_test,
            'y_pred': y_pred,
            'X_test': X_test_scaled,
            'model_type': model_type
        }

    def save_model(self, filepath='model_klasifikasi.pkl'):
        """Simpan model ke file"""
        if self.model is None:
            raise ValueError("Model belum di-train!")

        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns,
            'target_column': self.target_column
        }

        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

        print(f"✅ Model disimpan ke: {filepath}")

    def load_model(self, filepath='model_klasifikasi.pkl'):
        """Load model dari file"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoders = model_data['label_encoders']
        self.feature_columns = model_data['feature_columns']
        self.target_column = model_data['target_column']

        print(f"✅ Model dimuat dari: {filepath}")

    def predict(self, X_new):
        """Prediksi data baru"""
        if self.model is None:
            raise ValueError("Model belum di-load atau di-train!")

        # Preprocess data baru (sama seperti training)
        X_scaled = self.scaler.transform(X_new)
        predictions = self.model.predict(X_scaled)

        # Decode jika target di-encode
        if self.target_column in self.label_encoders:
            predictions = self.label_encoders[self.target_column].inverse_transform(
                predictions)

        return predictions


# ============================================
# CONTOH PENGGUNAAN
# ============================================
if __name__ == "__main__":
    # Inisialisasi classifier
    ml = MLClassifier()

    # Path ke file Excel (sesuaikan dengan file Anda)
    excel_file = "dkpp-od_19752_jml_kejadian_penyakit_hewan_rabies_pada_komoditas__v2_data.xlsx"

    if os.path.exists(excel_file):
        # Load data
        df = ml.load_excel(excel_file)

        # Tentukan kolom target (sesuaikan dengan dataset Anda)
        # Jika tidak ditentukan, akan menggunakan kolom terakhir
        # atau tentukan manual: target_col = "nama_kolom_target"
        target_col = df.columns[-1]

        # Preprocess
        X, y, df_processed = ml.preprocess_data(df, target_column=target_col)

        # Train model
        results = ml.train_model(X, y, model_type='random_forest')

        # Simpan model
        ml.save_model('model_klasifikasi.pkl')

        print("\n" + "="*50)
        print("✅ Program selesai! Model siap digunakan.")
        print("="*50)
    else:
        print(f"❌ File Excel tidak ditemukan: {excel_file}")
        print("   Pastikan file Excel ada di folder yang sama dengan script ini.")
