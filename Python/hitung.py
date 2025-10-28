def Faktor(a):
    if a == 1:
        return (a)
    else:
        return (a*Faktor(a-1))
    
def faktor(b):
    if b == 1:
        return (b)
    else:
        return (b*faktor(b-1))

 
Angka1 = int(input('Masukan Angka Faktorial : '))
Angka2 = int(input('Masukan Angka Faktorial : '))

hasil = Faktor(Angka1) + Faktor(Angka2)

print(f'Faktor Dari {faktor(Angka1)}!')
print(f'Faktor Dari {faktor(Angka2)}!')
print('=' * 12)
print(f'Hasil dari {Angka1}! dan {Angka2}! = {hasil}')
    