import json
import os
from jabol import *

file = "db/db.json"

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
    for i in range(1, len(db)+1):
        if db[f"{i}"]["verified"] == False:
            toVerify.append([i, db[f"{i}"]])
    for i in toVerify:
        print(i)
        print("Czy chcesz zweryfikowac ten wpis? Pamietaj zeby sprawdzic czy obraz w odpowiednim folderze sie zgadza! (Y/N)")
        x = input().lower()
        if x == "y":
            print(i[0], "zweryfikowano")
            edit_database(i[0], "verified", True, file)
        elif x == "n":
            print(i[0], "odrzucono")
            removeentry(file, i[0])
        else:
            print("To nie jest poprawna wartosc!")

def main():
    x = countUnverified(file)
    print('''
   mmm         #             ""#    ""#
     #   mmm   #mmm    mmm     #      #    m   m  mmmmm
     #  "   #  #" "#  #" "#    #      #    #   #  # # #
     #  m"""#  #   #  #   #    #      #    #   #  # # #
 "mmm"  "mm"#  ##m#"  "#m#"    "mm    "mm  "mm"#  # # #
    ''')
    print("Witaj w programie do zarzadzania bazą danych Jabollum!")
    print(f"Masz {x} wpisow do zweryfikowania.")
    choice = input("Wybierz opcje: \n 1. Dodaj nowy wpis \n 2. Wyswietl baze danych\n 3. Usun wpis\n 4. Weryfikuj wpisy \n 5. Wyjdz\n")
    match choice:
        case "1":
            print(addentry(file))
            main()
        case "2":
            print(printfile(file))
            main()
        case "3":
            removeentry(file, input("Podaj id wpisu do usuniecia: "))
            print("Wpis usuniety!")
            main()
        case "4":
            verifyEntries(file)
            main()
        case "5":
            exit()

if __name__ == "__main__":
    main()