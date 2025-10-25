import tensorflow as tf
from keras import layers, models

# 1️⃣ Load dataset MNIST (gambar angka 0-9)
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()

# 2️⃣ Normalisasi (biar nilai piksel antara 0–1)
x_train, x_test = x_train / 255.0, x_test / 255.0

# 3️⃣ Bangun model sederhana (3 layer)
model = models.Sequential([
    layers.Flatten(input_shape=(28, 28)),       # ubah 2D jadi 1D
    layers.Dense(128, activation='relu'),       # hidden layer
    layers.Dropout(0.2),                        # mencegah overfitting
    layers.Dense(10, activation='softmax')      # output 10 kelas (0–9)
])

# 4️⃣ Kompilasi model
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# 5️⃣ Latih model
model.fit(x_train, y_train, epochs=5, validation_data=(x_test, y_test))

# 6️⃣ Evaluasi akurasi
test_loss, test_acc = model.evaluate(x_test, y_test, verbose=2)
print(f'\nAkurasi model di data test: {test_acc:.4f}')

# 7️⃣ Simpan model (opsional)
model.save("mnist_model.h5")
print("Model disimpan ke mnist_model.h5 ✅")
