import os,time

while True:
    os.system ('cls' if os.name == 'nt' else 'clear')
    print('='*15, 'Boobs', '='*15) 
    print('A Cup - B Cup - C Cup - D Cup - G Cup')
    size = input('Pilih Cup : ').strip().lower()
    if size == 'a' or size == 'a cup':
        acup = ' '
        print(f'({acup} . {acup})  ({acup} . {acup})')
        print('='*37)
        break
    elif size == 'b' or size == 'b cup':
        bcup = '  '
        print(f'({bcup} . {bcup})  ({bcup} . {bcup})')
        print('='*37)
        break
    elif size == 'c' or size == 'c cup':
        ccup = '   '
        print(f'({ccup} . {ccup})  ({ccup} . {ccup})')
        print('='*37)
        break
    elif size == 'd' or size == 'd cup':
        dcup = '    '
        print(f'({dcup} . {dcup})  ({dcup} . {dcup})')
        print('='*37)
        break
    elif size == 'g' or size == 'g cup':
        gcup = '      '
        print(f'({gcup} . {gcup})  ({gcup} . {gcup})')
        print('='*37)
        break
    else:
        print('Bro, kamu over input. kamu mau sebesar apa?')
        print('='*37)
        time.sleep(3)
        