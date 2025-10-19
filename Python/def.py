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


def MenNum():
    TehNum = {
        '1': 'Teh Manis     : Rp. 3.000',
        '2': 'Teh Tawar     : Rp. 2.000',
        '3': 'Teh Hijau     : Rp. 5.000',
        '4': 'Teh Oloong    : Rp. 5.000',
        '5': 'Teh Hitam     : RP. 7.000'
    }
    CofNum = {
        '1': 'Americano    : Rp. 8.000',
        '2': 'Cappucino    : Rp. 10.000',
        '3': 'Creamy Mokka : Rp. 10.000',
        '4': 'Sugar Lemon  : Rp. 8.000',
        '5': 'Kopi Hitam   : RP. 5.000'
    }
    ModNum = {
        '1': 'Soft Drinks     : Rp. 8.000',
        '2': 'Rainbow Shot    : Rp. 15.000',
        '3': 'Matcha Latte    : Rp. 25.000',
        '4': 'Cendol Dawets   : Rp. 5.000',
        '5': 'Cocktail        : RP. 150.000'
    }
    return {'Tea': TehNum, 'Kopi': CofNum, 'SD': ModNum}


while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    print('=' * 40)
    print('Selamat Datang di Restoran Pondok Wenak')
    print('=' * 40)
    print('Silakan Pilih Menu            ')
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
        SubPil = input('Silahkan Pilih dengan Angka : ')

        if SubPil == '1':
            os.system('cls' if os.name == 'nt' else 'clear')
            print('==========================')
            print('     Menu Tradisional     ')
            print('==========================')
            for key, value in MakMenu['Trad'].items():
                print(f'{key}. {value}')
            PilMak = input('Pilih Sesuai Angka : ')

        elif SubPil == '2':
            os.system('cls' if os.name == 'nt' else 'clear')
            print('==========================')
            print('       Menu Modern        ')
            print('==========================')
            for key, value in MakMenu['Mod'].items():
                print(f'{key}. {value}')
            PilMak = input('Pilih Sesuai Angka : ')

    elif PilHan == '3':
        os.system('cls' if os.name == 'nt' else 'clear')
        print('====================================')
        print('         Silakan Pilih Menu         ')
        print('1.) Tea - 2.) Coffe - 3.) Softdrinks')
        print('====================================')
        SoftMinum = MenNum()
        SubPil = input('Silahkan Pilih dengan Angka : ')

        if SubPil == '1':
            for key, value in SoftMinum['Tea'].items():
                print(f'{key}. {value}')
            PilNUm = input('Pilih Sesuai Angka : ')

        elif SubPil == '2':
            for key, value in MenNum['Kopi'].items():
                print(f'{key}. {value}')
            PilNUm = input('Pilih Sesuai Angka : ')

        elif SubPil == '3':
            for key, value in MenNum['SD'].items():
                print(f'{key}. {value}')
            PilNUm = input('Pilih Sesuai Angka : ')
