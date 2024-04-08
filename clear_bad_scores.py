#!/usr/bin/python3
import jabol
import yaml

with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

db = jabol.readfile(CONFIG["main_db_file"])

for entry in db:
    index = 0
    for s in db[entry]["scores"]:
        s = int(s)
        if s < 0 or s > 10:
            del db[entry]["scores"][index]
            del db[entry]["votes"][index]
        index += 1
    db[entry]["score"] = sum(db[entry]["scores"]) / len(db[entry]["scores"])
    

    

jabol.save_database(CONFIG["main_db_file"], db)