import os
os.system('cls' if os.name == 'nt' else 'clear')
while True:
    A = float(input("Masukkan nilai A: "))
    B = float(input("Masukkan nilai B: "))

# Proses
    if A > B:
        C = A * B
        D = C * C
        print("Karena A lebih besar dari B")
        print("Nilai D =", D)
        print("Nilai C =", C)
    else:
        C = A + B
        D = C * C
        print("Karena A tidak lebih besar dari B")
        print("Nilai C =", C)
        print("Nilai D =", D)
        continue