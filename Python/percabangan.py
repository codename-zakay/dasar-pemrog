import os
os.system('cls' if os.name == 'nt' else 'clear')
gaji = 300000*30
lembur = 3500  # /jam
Total = "gaji + tunjangan_jabatan + tunjangan_pendidikan + lembur"

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
if pendidikan == "SMA":
    tunjangan_pendidikan = 5/100*gaji
elif pendidikan == "D1":
    tunjangan_pendidikan = 10/100*gaji
elif pendidikan == "D3":
    tunjangan_pendidikan = 20/100*gaji
elif pendidikan == "S1":
    tunjangan_pendidikan = 30/100*gaji
else:(0)

print("===Struk Gaji Karyawan===")
print(f"Nama Karyawan : {Nama_Karyawan}")
print(f"Gaji Pokok : Rp. {gaji:,}")
print(f"Tunjangan Jabatan : Rp. {tunjangan_jabatan:,}")
print(f"Tunjangan Pendidikan : Rp. {tunjangan_pendidikan:,}")
Total = int(gaji_pokok + tunjangan_jabatan + tunjangan_pendidikan + Uang_lembur)
print(f"Total Gaji Bulan ini : Rp. {Total:,}")
print('='*25)

