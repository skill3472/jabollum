#!/usr/bin/python3
from jabol import *

a = input('Podaj sciezke do bazy danych glownej: ')
b = input('Podaj sciezke do bazy danych recenzji: ')
print(purge_db(a, b))