import os
os.system('cls' if os.name == 'nt' else 'clear')
gaji = 300000*30
lembur = 3500  # /jam

Nama_Karyawan = input("Masukkan Nama Karyawan : ")
tunjangan_jabatan = input("Masukkan Golongan Jabatan (1/2/3) : ")
pendidikan = input("Masukkan Pendidikan (SMA/D1/D3/S1) : ")
jumlah_jam_kerja = input("Jumlah jam kerja : ")
Jam_lembur = input("Jumlah jam lembur : ")
Uang_lembur = int(Jam_lembur) * lembur

# mapping Tunjangan jabatan
tunjab ={
"1": 0.05, # 5%
"2": 0.1,  # 10%
"3": 0.15  # 15% 
}

if tunjangan_jabatan not in tunjab:
    raise ValueError("Golongan Jabatan tidak valid. Harus 1, 2, atau 3.")

# library Pendidikan
tunjpend = {
"SMA": 0.025, # 2.5%
"D1": 0.05,  # 5%
"D3": 0.2, # 7.5%
"S1": 0.3    # 10%
}

if pendidikan not in tunjpend:
    raise ValueError("Pendidikan tidak valid. Harus SMA, D1, D3, atau S1.")


Total = "gaji + tunjangan_jabatan + tunjangan_pendidikan + lembur"
print("===Struk Gaji Karyawan===")
print(f"Nama Karyawan : {Nama_Karyawan}")
print(f"Gaji Pokok : Rp. {gaji:,}")
print(f"Tunjangan Jabatan : Rp. {tunjangan_jabatan:,}")
print(f"Tunjangan Pendidikan : Rp. {tunjangan_pendidikan:,}")
Total = int(gaji_pokok + tunjangan_jabatan + tunjangan_pendidikan + Uang_lembur)
print(f"Total Gaji Bulan ini : Rp. {Total:,}")
print('='*25)