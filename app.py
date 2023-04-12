from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import json
import os

file = "db/db.json"
UPLOAD_FOLDER = 'static/images/unverified/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp'}

app = Flask(__name__, template_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.config['SECRET_KEY'] = open("secret.txt", "r").read()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_database(database):
    with open(file, "w") as f:
        json.dump(database, f, indent=4)

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

@app.route("/submit")
def submit_suggestion():
    return app.send_static_file('submit.html')

@app.route("/submit/submit-suggestion", methods=["GET", "POST"])
def submit_suggestion_post():
    with open(file, "r") as f:
        database = json.load(f)
    new_entry = {}
    if request.method == "POST":
        image = request.files.get("image")
        if not image:
            flash('No file part')
            return redirect("/submit")
        if not allowed_file(image.filename):
            flash("Invalid file type")
            return redirect("/submit")
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        new_entry["image"] = image_path
        new_entry["name"] = request.form["name"]
        new_entry["shops"] = request.form["shops"]
        new_entry["score"] = int(request.form["score"])
        new_entry["scores"] = [new_entry["score"]]
        new_entry["votes"] = []
        new_entry["verified"] = False
        database.update(new_entry)
        save_database(database)
        return redirect(url_for("submit_suggestion_post"))
    return render_template("submit.html", submitted=True)

if(__name__ == '__main__'):
    app.run(debug=True)