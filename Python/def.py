import os


def MenBuh():
    Buahn = {
        '1': 'Apel      : Rp. 7.000',
        '2': 'Pisang    : Rp. 5.000',
        '3': 'Anggur    : Rp. 9.000',
        '4': 'Semangka  : Rp. 5.000',
        '5': 'Melon     : RP. 5.000'
    }
    return Buahn

def MenMak():
    MakTrad = {
        '1': 'Karedok       : Rp. 10.000',
        '2': 'Ketoprak      : Rp. 12.000',
        '3': 'Gudeg         : Rp. 10.000',
        '4': 'Cah Kangkung  : Rp. 9.000',
        '5': 'Ayam POP      : Rp. 18.000',
        '6': 'Rendang       : Rp. 20.000'
    }
    MakMod = {
        '1': 'Pizza         : Rp. 45.000',
        '2': 'Hamburg       : Rp. 28.000',
        '3': 'Kebab         : Rp. 21.000',
        '4': 'Fried Chicken : Rp. 10.000',
        '5': 'Spagetti      : Rp. 15.000',
        '6': 'Mac n Cheese  : Rp. 25.000'
    }
    return {'Trad': MakTrad, 'Mod': MakMod}


while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    print('=' * 40)
    print('Selamat Datang di Restoran Pondok Wenak')
    print('=' * 40)
    print(         'Silakan Pilih Menu            ')
    print('1.) Menu Buah')
    print('2.) Menu Makanan')
    print('3.) Menu Minuman')
    PilHan = input('Masukan Angka untuk memilih Menu : ')

    if PilHan == '1':
        os.system('cls' if os.name == 'nt' else 'clear')
        print('====================================')
        print('         Silakan Pilih Menu         ')
        print('====================================')
        BuAh = MenBuh()
        for key, value in BuAh.items():
            print(f'{key}. {value}')
        FrBuh = input('Pilih Sesuai Angka : ')
    elif PilHan == '2':
        os.system('cls' if os.name == 'nt' else 'clear')
        print('====================================')
        print('         Silakan Pilih Menu         ')
        print('    1.) Tradisional - 2.) Modern    ')
        print('====================================')
        MakMenu = MenMak()
        SubPil = int(input('Silahkan Pilih dengan Angka : '))

        if SubPil == 1:
            os.system('cls' if os.name == 'nt' else 'clear')
            print('==========================')
            print('     Menu Tradisional     ')
            print('==========================')
            for key, value in MakMenu['Trad'].items():
                print(f'{key}. {value}')
            PilMak = input('Pilih Sesuai Angka : ')
