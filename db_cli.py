import json
import os

file = "db/db.json"

def readfile(file):
    if os.path.exists(file) and os.stat(file).st_size > 0:
        with open(file, "r") as f:
            return json.load(f)
    else:
        return []
    
def printfile(file):
    print(readfile(file))

def appendfile(file, data):
    temp = readfile(file)
    entry_id = str(len(temp) + 1)
    temp[entry_id] = data
    with open(file, "w") as f:
        json.dump(temp, f, indent=4)

def addentry(file):
    data = {}
    data["image"] = input("Podaj nazwe pliku z obrazkiem (format \"image/obrazek.png\"): ")
    data["name"] = input("Podaj nazwe napoju: ")
    data["shops"] = input("Podaj sklepy w ktorych mozna kupic napoj, oddzielone przecinkiem i spacja: ")
    data["score"] = int(input("Podaj swoja ocene napoju, od 1 do 10: "))
    data["price"] = float(input("Podaj cene napoju w PLN: "))
    data["scores"] = [].append(data["score"])
    data["votes"] = []
    verified = input("Podaj status weryfikacji (Y/N): ")
    if(verified == "Y"):
        data["verified"] = True
    else:
        data["verified"] = False
    appendfile(file, data)
    return "Dodano wpis!"

def removeentry(file, id):
    temp = readfile(file)
    del temp[f"{id}"]
    with open(file, "w") as f:
        json.dump(temp, f, indent=4)

def main():
    print('''
   mmm         #             ""#    ""#
     #   mmm   #mmm    mmm     #      #    m   m  mmmmm
     #  "   #  #" "#  #" "#    #      #    #   #  # # #
     #  m"""#  #   #  #   #    #      #    #   #  # # #
 "mmm"  "mm"#  ##m#"  "#m#"    "mm    "mm  "mm"#  # # #
    ''')
    print("Witaj w programie do zarzadzania bazą danych Jabollum!")
    choice = input("Wybierz opcje: \n 1. Dodaj nowy wpis \n 2. Wyswietl baze danych\n 3. Usun wpis\n 4. Wyjdz\n")
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
            exit()

if __name__ == "__main__":
    main()