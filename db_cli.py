import json
import os

file = "db/db.json"

def readfile(file):
    if os.path.exists(file) and os.stat(file).st_size > 0:
        with open(file, "r") as f:
            return json.load(f)
    else:
        return []

def appendfile(file, data):
    temp = readfile(file)
    temp[data["id"]] = data
    with open(file, "w") as f:
        json.dump(temp, f, indent=4)

def addentry(file):
    data = {}
    data["image"] = input("Podaj nazwe pliku z obrazkiem (format \"image/obrazek.png\"): ")
    data["name"] = input("Podaj nazwe napoju: ")
    data["shops"] = input("Podaj sklepy w ktorych mozna kupic napoj, oddzielone przecinkiem i spacja: ")
    data["score"] = int(input("Podaj swoja ocene napoju, od 1 do 10: "))
    verified = input("Podaj status weryfikacji (Y/N): ")
    if(verified == "Y"):
        data["verified"] = True
    else:
        data["verified"] = False
    appendfile(file, data)

addentry(file)