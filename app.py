from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from jabol import *
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


@app.route('/')
def main():
    return app.send_static_file('index.html')


@app.route('/archive')
def archive():
    with open(file, "r") as f:
        data = json.load(f)
    verified_entries = []
    for entry in data:
        data[entry]["price"] = "{:.2f}".format(data[entry]["price"])
        if data[entry]["verified"]:
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
        save_database(file, database)
    return render_template("jabol_page.html", jabol_data=database[f"{id}"], id=id)


@app.route("/submit", methods=["POST", "GET"])
def submit_suggestion():
    if request.method == "GET":
        return app.send_static_file('submit.html')
    elif request.method == "POST":
        new_entry = {}
        user_id = str(request.remote_addr)
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
        new_entry["price"] = float(request.form["price"])
        new_entry["score"] = int(request.form["score"])
        new_entry["scores"] = [new_entry["score"]]
        new_entry["votes"] = [user_id]
        new_entry["description"] = request.form["description"]
        new_entry["verified"] = False
        appendfile(file, new_entry)
        return render_template("submit.html", submitted=True)
    else:
        return "Invalid method! Use POST or GET on this page."

if __name__ == '__main__':
    app.run(debug=True)