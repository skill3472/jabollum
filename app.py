from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from jabol import *
import json
import os
from datetime import datetime

file = "db/db.json"
review_file = "db/reviews.json"
UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp'}

app = Flask(__name__, template_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.config['SECRET_KEY'] = open("secret.txt", "r").read()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def main():
    return render_template('index.html')


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


@app.route('/archive/<id>', methods=["GET", "POST"])
def id(id):
    if request.method == "GET":
        with open(file, "r") as f:
            data = json.load(f)
        with open(review_file, "r") as f:
            review_data_unfiltered = json.load(f)
        review_data = []
        for i in review_data_unfiltered:
            if review_data_unfiltered[i]["drink_id"] == id and review_data_unfiltered[i]["verified"]:
                review_data.append(review_data_unfiltered[i])
        return render_template('jabol_page.html', jabol_data=data[f"{id}"], id=id, review_data=review_data)
    elif request.method == "POST":
        new_entry = {}
        new_entry["drink_id"] = id
        new_entry["name"] = request.form["name"]
        new_entry["review"] = request.form["review"]
        new_entry["date"] = datetime.now().strftime("%d.%m.%Y - %H:%M")
        new_entry["uid"] = str(request.remote_addr)
        new_entry["verified"] = False
        appendfile(review_file, new_entry)
        flash("Review sent, waiting for verification!")
        return redirect(f"/archive/{id}")
    else:
        return "Invalid method!"

@app.route("/submit", methods=["POST", "GET"])
def submit_suggestion():
    if request.method == "GET":
        return render_template('submit.html', submitted=False)
    elif request.method == "POST":
        db = readfile(file)
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
        new_filename = str(len(db) + 1) + filename
        old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        image.save(old_image_path)
        os.rename(old_image_path, image_path)
        new_entry["image"] = f'images/{new_filename}'
        new_entry["name"] = request.form["name"]
        new_entry["shops"] = request.form["shops"]
        new_entry["price"] = float(request.form["price"])
        new_entry["ac"] = float(request.form["ac"])
        new_entry["vol"] = float(request.form["vol"])
        new_entry["score"] = int(request.form["score"])
        new_entry["scores"] = [new_entry["score"]]
        new_entry["votes"] = [user_id]
        new_entry["description"] = request.form["description"]
        new_entry["verified"] = False
        appendfile(file, new_entry)
        flash("Wyslano sugestie!")
        return redirect("/submit")
    else:
        return "Invalid method! Use POST or GET on this page."

if __name__ == '__main__':
    app.run(debug=True)