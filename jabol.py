import os
import json
import bcrypt
import re

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

def purge_db(file1, file2, file3):
    db1 = readfile(file1)
    db2 = readfile(file2)
    db3 = readfile(file3)
    x = input('TEN PROGRAM KASUJE OBIE BAZY DANYCH. OBIE KURWA BAZY DANYCH.\nCZY NA PEWNO CHCESZ TO ZROBIC IDIOTO? (ABY POTWIERDZIC, WPISZ "JESTEM DEBILEM"): ')
    if x == 'JESTEM DEBILEM':
        for i in range(1, int(list(db1)[-1])+1):
            if db1.get(f"{i}") != None:
                removeentry(file1, i)
        for i in range(1, int(list(db2)[-1])+1):
            if db2.get(f"{i}") != None:
                removeentry(file2, i)
        for i in range(1, int(list(db3)[-1])+1):
            if db3.get(f"{i}") != None:
                removeentry(file3, i)
        return 'Wyczyszczono wszystkie bazy danych!'
    else:
        return 'Anulowano.'
    
def hash_password(plain_text_password):
    plain_text_password = plain_text_password.encode('utf-8')
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

def check_password(plain_text_password, hashed_password):
    plain_text_password = plain_text_password.encode('utf-8')
    hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_text_password, hashed_password)

def get_user_data(users_file, session_uid):
    users = readfile(users_file)
    user = session_uid
    return users[f'{user}']

def get_admin_list(users_file):
    list = []
    users = readfile(users_file)
    for uid in users:
        if users[f"{uid}"]["admin"] == True:
            list.append(uid)
    return list

def get_pro_list(users_file):
    list = []
    users = readfile(users_file)
    for uid in users:
        if users[f"{uid}"]["pro"] == True:
            list.append(uid)
    return list

def check_ip(string):
	ex = '^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
	res = re.findall(ex, string)
	if len(res) > 0:
		return True
	else:
		return False

def add_points(uid, points_to_add, users_file): # Note: you can also REMOVE points with this function, using a negative number
    usr_data = get_user_data(users_file, uid)
    usr_data['points'] += points_to_add
    edit_database(uid, 'points', usr_data['points'], users_file)