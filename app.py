from flask import Flask, render_template, request, flash, redirect, url_for, abort
from werkzeug.utils import secure_filename
from jabol import *
import json
import os
from datetime import datetime
import yaml
import requests

file = "db/db.json"
review_file = "db/reviews.json"
UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp'}
VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'

with open("secrets.yaml", "r") as f:
    SECRETS = yaml.safe_load(f)

app = Flask(__name__, template_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.config['SECRET_KEY'] = SECRETS['flask_secret']


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
            data[entry]["idx"] = entry
            data[entry]["score"] = round(data[entry]["score"], 2)
            verified_entries.append(data[entry])
    return render_template('archive.html', table_data=verified_entries)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/donate')
def donate():
    return render_template('donate.html')

@app.route('/archive/<id>', methods=["GET", "POST"])
def id(id):
    with open(file, "r") as f:
        data = json.load(f)
    if id in data.keys():
        if request.method == "GET":
            with open(review_file, "r") as f:
                review_data_unfiltered = json.load(f)
            review_data = []
            for i in review_data_unfiltered:
                if review_data_unfiltered[i]["drink_id"] == id and review_data_unfiltered[i]["verified"]:
                    review_data.append(review_data_unfiltered[i])
            for i in data:
                data[f"{i}"]["score"] = round(data[f"{i}"]["score"], 2)
            return render_template('jabol_page.html', jabol_data=data[f"{id}"], id=id, review_data=review_data, isChild=True, site_key=SECRETS['site_key'])
        elif request.method == "POST":
            # response = request.form['g-recaptcha-response']
            # verify_response = requests.post(url=f'{VERIFY_URL}?secret={SECRETS["secret_key"]}&response={response}')
            # if verify_response['success'] == False:
            #     abort(401)
            new_entry = {}
            new_entry["drink_id"] = id
            new_entry["name"] = request.form["name"]
            new_entry["review"] = request.form["review"]
            new_entry["date"] = datetime.now().strftime("%d.%m.%Y - %H:%M")
            new_entry["uid"] = str(request.headers['x-real-ip'])
            new_entry["verified"] = False
            appendfile(review_file, new_entry)
            flash("Recenzja wysłana, czekaj na weryfikację!")
            return redirect(f"/archive/{id}")
        else:
            return "Nieprawidłowa metoda! Użyj POST, albo GET."
    else:
        return "Nieprawidłowe id!"
    
@app.route("/archive/<id>/submit-vote", methods=["POST"])
def submit_vote(id):
    # response = request.form['g-recaptcha-response']
    # verify_response = requests.post(url=f'{VERIFY_URL}?secret={SECRETS["secret_key"]}&response={response}')
    # if verify_response['success'] == False:
    #     abort(401)
    print("Jabol o tym id zostal oceniony:", id)
    with open(file, "r") as f:
        database = json.load(f)
    user_id = str(request.headers['x-real-ip'])
    score = int(request.form["score"])
    if user_id not in database[f"{id}"]["votes"]:
        database[f"{id}"]["votes"].append(user_id)
        database[f"{id}"]["scores"].append(score)
        database[f"{id}"]["score"] = sum(database[f"{id}"]["scores"]) / len(database[f"{id}"]["scores"])
        save_database(file, database)
    else:
        flash("Już oceniałeś tego jabola!")
    return redirect(f"/archive/{id}")

@app.route("/submit", methods=["POST", "GET"])
def submit_suggestion():
    if request.method == "GET":
        return render_template('submit.html', submitted=False, site_key=SECRETS['site_key'])
    elif request.method == "POST":
        db = readfile(file)
        new_entry = {}
        user_id = str(request.remote_addr)
        image = request.files.get("image")
        if not image:
            flash('Brak pliku!')
            return redirect("/submit")
        if not allowed_file(image.filename):
            flash("Nieprawidłowy typ pliku!")
            return redirect("/submit")
        filename = secure_filename(image.filename)
        new_filename = str(len(db) + 1) + request.form["name"] + filename
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
        if len(request.form["description"]) > 0:
            new_entry["description"] = request.form["description"]
        else:
            new_entry["description"] = "Brak opisu."
        new_entry["verified"] = False
        appendfile(file, new_entry)
        flash("Wyslano sugestie!")
        return redirect("/submit")
    else:
        return "Nieprawidłowa metoda! Użyj POST, albo GET."

@app.route("/discord")
def discord():
    return redirect('https://discord.gg/8Ugkr4d5Ax')

if __name__ == '__main__':
    app.run(debug=True)