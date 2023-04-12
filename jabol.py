import os
import json

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
    
def removeentry(file, id):
    temp = readfile(file)
    del temp[f"{id}"]
    with open(file, "w") as f:
        json.dump(temp, f, indent=4)

def save_database(file, database):
    with open(file, "w") as f:
        json.dump(database, f, indent=4)