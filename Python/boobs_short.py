import os,time
csze = {
    'a': ' ',
    'b': '  ',
    'c': '   ',
    'd': '    ',
    'g': '     ',
    'a cup': ' ',
    'b cup': '  ',
    'c cup': '   ',
    'd cup': '    ',
    'g cup': '     ',
}

while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    print('=' * 15 + ' Boobs ' + '=' * 15)
    print('A Cup - B Cup - C Cup - D Cup - G Cup')
    size = input('Pilih Ukurannya : ').strip().lower()

    if size in csze:
        boobs = csze[size]
        print(f'({boobs} . {boobs})  ({boobs} . {boobs})')
        print('='*37)
        break
    else:
        print('Bro Ukuranya Gak VALID!!')
        print('='*37)
        time.sleep(2)
