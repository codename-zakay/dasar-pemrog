import os

while True:
    # Membersihkan layar setiap kali program dijalankan
    os.system('cls' if os.name == 'nt' else 'clear')

    #input data
    Nama_Siswa = input("Masukkan Nama Siswa : ").strip()
    Nis = input("Masukkan NIS : ").strip()
    Jurusan= input("Masukkan Jurusan : ").strip().upper()

#pilihan jurusan
    if Jurusan.upper() == "SI":
        Nama_Jurusan = "Sistem Informasi"
        Harga= 2400000
    elif Jurusan.upper() == "SIA":
        Nama_Jurusan = "Sistem Informasi Akuntansi"
        Harga= 2000000
    else : 
        print("Jurusan Tidak Tersedia, masukan ulang")
        input("Tekan Enter untuk mengulang....")
        continue

    #struk pembayaran
    os.system('cls' if os.name == 'nt' else 'clear')
    print("="*25)
    print("      STRUK PEMBAYARAN     ")
    print("="*25)
    print("Nama Siswa :", Nama_Siswa)
    print(f"Nis  :", Nis)
    print("Jurusan :",Jurusan)
    print("Harga : Rp{:,.0f}".format(Harga).replace(",", "."))
    print('='*25)

# Tanya apakah ingin input data lagi
    ulang = input("Apakah ingin input data lagi? (y/n): ").strip().lower()
    if ulang != 'y':
        print("Terima kasih! Program selesai.")
        break