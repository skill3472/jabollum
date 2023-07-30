#!/usr/bin/python3
import json
import os
from jabol import *
from datetime import datetime, timedelta, timezone
import shutil
import yaml

FILE = "db/db.json"
reviews_file = "db/reviews.json"
BACKUP_PATH = "db/backups/"
USERS_FILE = 'db/users.json'

with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

UTC_OFFSET = CONFIG['utc_offset']
tzinfo = timezone(timedelta(hours=UTC_OFFSET))

def addentry(file):
    data = {}
    data["image"] = input("Podaj nazwe pliku z obrazkiem (format \"image/obrazek.png\"): ")
    data["name"] = input("Podaj nazwe napoju: ")
    data["shops"] = input("Podaj sklepy w ktorych mozna kupic napoj, oddzielone przecinkiem i spacja: ")
    data["score"] = int(input("Podaj swoja ocene napoju, od 1 do 10: "))
    data["price"] = float(input("Podaj cene napoju w PLN: "))
    data["ac"] = float(input("Podaj moc napoju w %: "))
    data["vol"] = float(input("Podaj objetosc napoju w L: "))
    data["scores"] = [data["score"]]
    data["votes"] = ["127.0.0.1"]
    data["description"] = input("Podaj opis jabola: \n")
    verified = input("Podaj status weryfikacji (Y/N): ").lower()
    if verified == "y":
        data["verified"] = True
    elif verified == "n":
        data["verified"] = False
    else:
        return "Wartosc weryfikacji niepoprawna!"
    appendfile(file, data)
    return "Dodano wpis!"

def verifyEntries(file):
    db = readfile(file)
    toVerify = []
    for i in range(1, int(list(db)[-1])+1):
        if f"{i}" in db.keys() and db[f"{i}"]["verified"] == False:
            toVerify.append([i, db[f"{i}"]])
    for i in toVerify:
        print(i)
        print("Czy chcesz zweryfikowac ten wpis? Pamietaj zeby sprawdzic czy obraz w odpowiednim folderze sie zgadza! (Y/N)")
        x = input().lower()
        if x == "y":
            print(i[0], "zweryfikowano")
            edit_database(i[0], "verified", True, file)
            if check_ip(i[1]['votes'][0]) == False:
                add_points(i[1]['votes'][0], 50, USERS_FILE)
        elif x == "n":
            print(i[0], "odrzucono")
            removeentry(file, i[0])
        else:
            print("To nie jest poprawna wartosc!")

def verifyReviews(file):
    db = readfile(file)
    toVerify = []
    for i in range(1, int(list(db)[-1])+1):
        if f"{i}" in db.keys() and db[f"{i}"]["verified"] == False:
            toVerify.append([i, db[f"{i}"]])
    for i in toVerify:
        print(i[1]["name"])
        print(i[1]["review"])
        print("Czy chcesz zweryfikowac ta recenzje? (Y/N)")
        x = input().lower()
        if x == "y":
            print(i[0], "zweryfikowano")
            edit_database(i[0], "verified", True, reviews_file)
            add_points(i[1]['uid'], 50, USERS_FILE)
        elif x == "n":
            print(i[0], "odrzucono")
            removeentry(file, i[0])
        else:
            print("To nie jest poprawna wartosc!")

def backup(main_file, review_file, backup_location):
    date = datetime.now(tzinfo).strftime("%d-%m-%Y_%H-%M")
    path = backup_location + date
    try:
        os.makedirs(path)
        shutil.copy2(main_file, path)
        shutil.copy2(review_file, path)
        print('Backups made!')
    except OSError:
        pass

def main():
    x = countUnverified(FILE)
    y = countUnverified(reviews_file)
    print('''
   mmm         #             ""#    ""#
     #   mmm   #mmm    mmm     #      #    m   m  mmmmm
     #  "   #  #" "#  #" "#    #      #    #   #  # # #
     #  m"""#  #   #  #   #    #      #    #   #  # # #
 "mmm"  "mm"#  ##m#"  "#m#"    "mm    "mm  "mm"#  # # #
    ''')
    print("Witaj w programie do zarzadzania bazą danych Jabollum!")
    print(f"Masz {x} wpisow do zweryfikowania, oraz {y} recenzji do zweryfikowania.")
    choice = input("Wybierz opcje: \n 1. Dodaj nowy wpis \n 2. Wyswietl baze danych\n 3. Usun wpis\n 4. Weryfikuj wpisy\n 5. Weryfikuj recenzje\n 6. Backup\n 7. Wyjdz\n")
    match choice:
        case "1":
            print(addentry(FILE))
            main()
        case "2":
            print(printfile(FILE))
            main()
        case "3":
            removeentry(FILE, input("Podaj id wpisu do usuniecia: "))
            print("Wpis usuniety!")
            main()
        case "4":
            verifyEntries(FILE)
            main()
        case "5":
            verifyReviews(reviews_file)
            main()
        case "6":
            backup(FILE, reviews_file, BACKUP_PATH)
            main()
        case "7":
            exit()

if __name__ == "__main__":
    main()