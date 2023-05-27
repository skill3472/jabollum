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
    if temp:
        entry_id = str(int(list(temp)[-1]) + 1) # syf totalny, ale nie ruszac, bo dziala
    else:
        entry_id = "1"
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

def edit_database(entry_id, key, value, file):
    db = readfile(file)
    db[f"{entry_id}"][f"{key}"] = value
    save_database(file, db)

def countUnverified(file):
    db = readfile(file)
    count = 0
    for i in range(1, int(list(db)[-1])+1):
        key = db.get(f"{i}")
        if key != None and key["verified"] == False:
            count += 1
    return count