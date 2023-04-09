from flask import Flask, render_template, request
import json
import os

app = Flask(__name__, template_folder='static')

file = "db/db.json"

def save_database(database):
    with open(file, "w") as f:
        json.dump(database, f)

@app.route('/')
def main():
    return app.send_static_file('index.html')

@app.route('/archive')
def archive():
    with open(file, "r") as f:
        data = json.load(f)
    verified_entries = []
    for entry in data:
        print(f"{type(entry)}: {entry}")
        if data[entry]["verified"] == True:
            verified_entries.append(data[entry])
    print(f"Verified Entries: {verified_entries}")
    return render_template('archive.html', table_data=verified_entries)

@app.route('/archive/<id>')
def id(id):
    with open(file, "r") as f:
        data = json.load(f)
    print(data)
    return render_template('jabol_page.html', jabol_data=data[f"{id}"], id=id)

@app.route("/archive/<id>/submit-vote", methods=["POST"])
def submit_vote(id):
    print("id:", id)
    with open(file, "r") as f:
        database = json.load(f)
    user_id = str(request.remote_addr)
    score = int(request.form["score"])
    if user_id not in database[f"{id}"]["votes"]:
        database[f"{id}"]["votes"].append(user_id)
        database[f"{id}"]["scores"].append(score)
        database[f"{id}"]["score"] = sum(database[f"{id}"]["scores"]) / len(database[f"{id}"]["scores"])
        save_database(database)
    return render_template("jabol_page.html", jabol_data=database[f"{id}"], id=id)

if(__name__ == '__main__'):
    app.run(debug=True)