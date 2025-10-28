from keras.models import load_model
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# Load model
model = load_model("mnist_model.h5")

# Load gambar JPEG
img = Image.open("p.jpg").convert("L")  # ubah ke grayscale
img = img.resize((28, 28))                    # ukuran input model MNIST

# Ubah jadi array & normalisasi
img_array = np.array(img) / 255.0
img_array = 1 - img_array  # balik warna kalau angka putih di latar hitam
img_array = img_array.reshape(1, 28, 28)

# Prediksi
pred = model.predict(img_array)
hasil = np.argmax(pred)

# hasil
plt.imshow(img_array.reshape(28, 28), cmap='gray')
plt.title(f"Prediksi: {hasil}")
plt.show()

print(f"📸 Model menebak angka: {hasil}")
