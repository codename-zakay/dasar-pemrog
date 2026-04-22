import os
os.system('cls' if os.name == 'nt' else 'clear')

while True:
# Input dua bilangan
    A = float(input("Masukkan nilai A: "))
    B = float(input("Masukkan nilai B: "))

# Proses logika
    if A + B < 10:
        C = A - B
        D = 2 * C + B
        print("Karena A + B < 10")
        print("Nilai C =", C)
        print("Nilai D =", D)
    else:
        C = A + B
        D = 2 * C + B
        print("Karena A + B >= 10")
        print("Nilai C =", C)
        print("Nilai D =", D)
        continue