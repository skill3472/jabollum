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
    if os.path.exists(file) and os.stat(file).st_size > 0:
        with open(file, "r") as f:
            data = json.load(f)
    else:
        data = []
    data_with_id = [entry for entry in data if 'id' in entry]
    for entry in data_with_id:
        if entry["verified"] == False:
            data_with_id.remove(entry)
    return render_template('archive.html', table_data=data_with_id)

@app.route('/archive/<int:id>')
def id(id):
    with open(file, "r") as f:
        data = json.load(f)
    print(data)
    jabol_d = data[f"{id}"]
    return render_template('jabol_page.html', jabol_data=jabol_d)

@app.route("/archive/<int:id>/submit-vote", methods=["POST"])
def submit_vote(id):
    with open(file, "r") as f:
        database = json.load(f)
    user_id = request.remote_addr
    score = int(request.form["score"])
    #
    #   LOGIC REMOVED, WILL BE ADDED LATER
    #
    # return render_template("jabol_page.html", jabol_data=jabol_d)

if(__name__ == '__main__'):
    app.run(debug=True)