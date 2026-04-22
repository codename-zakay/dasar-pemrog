import os
os.system('cls' if os.name == 'nt' else 'clear')
gaji = 9000000
lembur = 3500  # /jam
Total = "gaji + tunjangan_jabatan + tunjangan_pendidikan + lembur"

print('='*15, 'Input Data', '='*15)
Nama_Karyawan = input("Masukkan Nama Karyawan : ")
tunjangan_jabatan = input("Masukkan Golongan Jabatan (1/2/3) : ")
pendidikan = input("Masukkan Pendidikan (SMA/D1/D3/S1) : ")
jumlah_jam_kerja = input("Jumlah jam kerja : ")
Jam_lembur = input("Jumlah jam lembur : ")
Uang_lembur = int(Jam_lembur) * lembur


# Kondisi Golongan Jabatan
if tunjangan_jabatan == "1":
    gaji_pokok = gaji
    tunjangan_jabatan = 5/100*gaji
elif tunjangan_jabatan == "2":
    gaji_pokok = gaji
    tunjangan_jabatan = 10/100*gaji
elif tunjangan_jabatan == "3":
    gaji_pokok = gaji
    tunjangan_jabatan = 15/100*gaji
else:
    (0)

# Kondisi Pendidikan
if pendidikan.upper() == "SMA":
    tunjangan_pendidikan = 0.05 * gaji
elif pendidikan.upper() == "D1":
    tunjangan_pendidikan = 0.10 * gaji
elif pendidikan.upper() == "D3":
    tunjangan_pendidikan = 0.20 * gaji
elif pendidikan.upper() == "S1":
    tunjangan_pendidikan = 0.30 * gaji
else:
    (0)

Total = gaji_pokok + tunjangan_jabatan + tunjangan_pendidikan + Uang_lembur

print("=== Struk Gaji Karyawan ===")
print(f"Nama Karyawan : {Nama_Karyawan}")
print(f"Gaji Pokok : Rp. {gaji:,.0f}")
print(f"Tunjangan Jabatan : Rp. {tunjangan_jabatan:,.0f}")
print(f"Tunjangan Pendidikan : Rp. {tunjangan_pendidikan:,.0f}")
print(f"Total Gaji Bulan ini : Rp. {Total:,}")
print('='*26)
