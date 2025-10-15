import os
os.system ('cls' if os.name == 'nt' else 'clear')
print('='*15, 'Boobs', '='*15) 
print('A Cup - B Cup - C Cup - D Cup - G Cup')
size = input('Pilih Cup : ').strip()
if size.lower == 'a' or 'a cup':
    acup = ' '
    print(f'({acup} . {acup})  ({acup} . {acup})')
elif size.lower ==  'b' or 'b cup':
    bcup = '   '
    print(f'({bcup} . {bcup})  ({bcup} . {bcup})')
elif size.lower == 'c' or 'c cup':
    ccup = '     '
    print(f'({ccup} . {ccup})  ({ccup} . {ccup})')