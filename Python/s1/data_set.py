"""
Machine Learning dengan Dataset
Contoh lengkap untuk membuat model ML dari dataset
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================
# CONTOH 1: Menggunakan Dataset Built-in (Iris)
# ============================================
print("=" * 50)
print("CONTOH 1: Dataset Iris (Built-in)")
print("=" * 50)

from sklearn.datasets import load_iris

# Load dataset Iris
iris = load_iris()
X = iris.data  # Features (sepal length, sepal width, petal length, petal width)
y = iris.target  # Labels (0: setosa, 1: versicolor, 2: virginica)

print(f"Jumlah data: {len(X)}")
print(f"Jumlah features: {X.shape[1]}")
print(f"Jumlah kelas: {len(np.unique(y))}")
print(f"Nama kelas: {iris.target_names}")

# Split data menjadi training dan testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Normalisasi data
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Buat dan latih model
model_iris = RandomForestClassifier(n_estimators=100, random_state=42)
model_iris.fit(X_train_scaled, y_train)

# Prediksi
y_pred = model_iris.predict(X_test_scaled)

# Evaluasi
accuracy = accuracy_score(y_test, y_pred)
print(f"\nAkurasi Model: {accuracy:.4f} ({accuracy*100:.2f}%)")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=iris.target_names))

# ============================================
# CONTOH 2: Menggunakan Dataset dari CSV
# ============================================
print("\n" + "=" * 50)
print("CONTOH 2: Dataset dari File CSV")
print("=" * 50)

# Contoh membuat dataset dummy (jika tidak ada file CSV)
# Dalam praktiknya, gunakan: df = pd.read_csv('nama_file.csv')

# Buat dataset contoh (Titanic-like dataset)
np.random.seed(42)
n_samples = 200

data = {
    'age': np.random.randint(18, 65, n_samples),
    'fare': np.random.uniform(10, 500, n_samples),
    'pclass': np.random.choice([1, 2, 3], n_samples),
    'sex': np.random.choice(['male', 'female'], n_samples),
    'survived': np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
}

df = pd.DataFrame(data)
print(f"\nDataset CSV (Contoh):")
print(df.head())
print(f"\nShape: {df.shape}")
print(f"\nInfo Dataset:")
print(df.info())

# Preprocessing untuk dataset CSV
# 1. Handle missing values (jika ada)
# df = df.dropna()  # atau df.fillna(value)

# 2. Encode categorical variables
le = LabelEncoder()
df['sex_encoded'] = le.fit_transform(df['sex'])

# 3. Pilih features dan target
features = ['age', 'fare', 'pclass', 'sex_encoded']
X_csv = df[features].values
y_csv = df['survived'].values

# Split data
X_train_csv, X_test_csv, y_train_csv, y_test_csv = train_test_split(
    X_csv, y_csv, test_size=0.2, random_state=42
)

# Normalisasi
scaler_csv = StandardScaler()
X_train_csv_scaled = scaler_csv.fit_transform(X_train_csv)
X_test_csv_scaled = scaler_csv.transform(X_test_csv)

# Buat dan latih model
model_csv = RandomForestClassifier(n_estimators=100, random_state=42)
model_csv.fit(X_train_csv_scaled, y_train_csv)

# Prediksi dan evaluasi
y_pred_csv = model_csv.predict(X_test_csv_scaled)
accuracy_csv = accuracy_score(y_test_csv, y_pred_csv)

print(f"\nAkurasi Model CSV: {accuracy_csv:.4f} ({accuracy_csv*100:.2f}%)")
print("\nClassification Report:")
print(classification_report(y_test_csv, y_pred_csv, 
                          target_names=['Not Survived', 'Survived']))

# ============================================
# VISUALISASI
# ============================================
print("\n" + "=" * 50)
print("Membuat Visualisasi...")
print("=" * 50)

# Confusion Matrix untuk dataset Iris
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Confusion Matrix Iris
cm_iris = confusion_matrix(y_test, y_pred)
sns.heatmap(cm_iris, annot=True, fmt='d', cmap='Blues', 
            xticklabels=iris.target_names,
            yticklabels=iris.target_names,
            ax=axes[0])
axes[0].set_title('Confusion Matrix - Dataset Iris')
axes[0].set_ylabel('True Label')
axes[0].set_xlabel('Predicted Label')

# Confusion Matrix CSV
cm_csv = confusion_matrix(y_test_csv, y_pred_csv)
sns.heatmap(cm_csv, annot=True, fmt='d', cmap='Greens',
            xticklabels=['Not Survived', 'Survived'],
            yticklabels=['Not Survived', 'Survived'],
            ax=axes[1])
axes[1].set_title('Confusion Matrix - Dataset CSV')
axes[1].set_ylabel('True Label')
axes[1].set_xlabel('Predicted Label')

plt.tight_layout()
plt.savefig('ml_results.png', dpi=150, bbox_inches='tight')
print("Visualisasi disimpan ke 'ml_results.png'")
# plt.show()  # Uncomment untuk menampilkan plot

# ============================================
# FUNGSI HELPER untuk Dataset Baru
# ============================================
def load_and_preprocess_csv(file_path, target_column, feature_columns=None):
    """
    Fungsi helper untuk load dan preprocess dataset CSV
    
    Parameters:
    - file_path: path ke file CSV
    - target_column: nama kolom target
    - feature_columns: list nama kolom features (None = semua kecuali target)
    """
    # Load CSV
    df = pd.read_csv(file_path)
    
    # Handle missing values
    df = df.dropna()
    
    # Encode categorical variables
    le_dict = {}
    for col in df.select_dtypes(include=['object']).columns:
        if col != target_column:
            le = LabelEncoder()
            df[col + '_encoded'] = le.fit_transform(df[col])
            le_dict[col] = le
    
    # Pilih features
    if feature_columns is None:
        feature_columns = [col for col in df.columns 
                          if col != target_column and not col.endswith('_encoded')]
        feature_columns += [col for col in df.columns if col.endswith('_encoded')]
    
    X = df[feature_columns].values
    y = df[target_column].values
    
    return X, y, df, le_dict

def train_model(X_train, y_train, model_type='random_forest'):
    """
    Fungsi untuk training model
    
    Parameters:
    - X_train: training features
    - y_train: training labels
    - model_type: jenis model ('random_forest', 'svm', 'logistic')
    """
    if model_type == 'random_forest':
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    # Tambahkan model lain sesuai kebutuhan
    
    model.fit(X_train, y_train)
    return model

print("\n" + "=" * 50)
print("SELESAI! ✅")
print("=" * 50)
print("\nTips:")
print("1. Untuk menggunakan dataset CSV sendiri, gunakan: pd.read_csv('file.csv')")
print("2. Pastikan dataset sudah bersih (handle missing values)")
print("3. Encode categorical variables sebelum training")
print("4. Selalu split data menjadi train/test")
print("5. Normalisasi data untuk hasil yang lebih baik")

