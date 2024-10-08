from flask import Flask, render_template, request, flash, redirect, url_for, abort, session, send_from_directory
from werkzeug.utils import secure_filename
from jabol import *
import json
import os
from datetime import datetime, timedelta, timezone
import yaml
import requests
import bcrypt
import urllib.parse

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp'}
VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'

with open("secrets.yaml", "r") as f:
    SECRETS = yaml.safe_load(f)

with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

UPLOAD_FOLDER = CONFIG["upload_folder"]
file = CONFIG["main_db_file"]
review_file = CONFIG["review_db_file"]
users_file = CONFIG["users_db_file"]
UTC_OFFSET = CONFIG['utc_offset']

app = Flask(__name__, template_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.config['SECRET_KEY'] = SECRETS['flask_secret']
app.secret_key = SECRETS['flask_secret']
app.permanent_session_lifetime = timedelta(days=7)
app.kofi_key = SECRETS['kofi_key']

user_colors = { # Nie użyte jeszcze nigdzie, może użyjemy
    "admin": "red",
    "donator": "gold",
    "none": "grey"
}

tzinfo = timezone(timedelta(hours=UTC_OFFSET))

FORBIDDEN = '403: Nie masz uprawnień do wejścia na tą stronę.'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def main():
    if "user" in session:
        loggedIn = True
    else:
        loggedIn = False
    return render_template('index.html', loggedIn=loggedIn)


@app.route('/archive')
def archive():
    if "user" in session:
        loggedIn = True
    else:
        loggedIn = False
    with open(file, "r") as f:
        data = json.load(f)
    verified_entries = []
    for entry in data:
        data[entry]["price"] = "{:.2f}".format(data[entry]["price"])
        if data[entry]["verified"]:
            data[entry]["idx"] = entry
            data[entry]["score"] = round(data[entry]["score"], 2)
            if data[entry]["score"] >= 7:
                data[entry]["color"] = 'green'
            elif data[entry]["score"] >= 4:
                data[entry]["color"] = 'orange'
            else:
                data[entry]["color"] = 'red'
            verified_entries.append(data[entry])
    return render_template('archive.html', table_data=verified_entries, loggedIn=loggedIn)

@app.route('/contact')
def contact():
    if "user" in session:
        loggedIn = True
    else:
        loggedIn = False
    return render_template('contact.html', loggedIn=loggedIn)

@app.route('/donate')
def donate():
    if "user" in session:
        loggedIn = True
    else:
        loggedIn = False
    return render_template('donate.html', loggedIn=loggedIn)

@app.route("/kofi-backend", methods = ["POST"])
def kofi_verify():
    req = urllib.parse.unquote_plus(request.data)[5:]
    if req["verification_token"] != app.kofi_key:
        return "Bad token"
    else:
        users = readfile(users_file)
        if req["message"] in [user["username"] for user in users]:
            users["message"]["pro"] = True
            for i in users:
                if users[f'{i}']["username"] == request.form["username"]:
                    uid = i
            edit_database(uid, "pro", True, users_file)
            return f"{req['message']} marked pro"
        else:
            return "No user registered with this name"

@app.route('/archive/<id>', methods=["GET", "POST"])
def id(id):
    with open(file, "r") as f:
        data = json.load(f)
    if id in data.keys():
        if request.method == "GET":
            if "user" in session:
                loggedIn = True
            else:
                loggedIn = False
            with open(review_file, "r") as f:
                review_data_unfiltered = json.load(f)
            review_data = []
            for i in review_data_unfiltered:
                if review_data_unfiltered[i]["drink_id"] == id and review_data_unfiltered[i]["verified"]:
                    review_data_unfiltered[i]['idx'] = i
                    review_data.append(review_data_unfiltered[i])
            for i in data:
                data[f"{i}"]["score"] = round(data[f"{i}"]["score"], 2)
                if data[f"{i}"]["score"] >= 7:
                    data[f"{i}"]["color"] = 'green'
                elif data[f"{i}"]["score"] >= 4:
                    data[f"{i}"]["color"] = 'orange'
                else:
                    data[f"{i}"]["color"] = 'red'
            admins = get_admin_list(users_file=users_file)
            pro = get_pro_list(users_file=users_file)
            registered = []
            for i in range(len(review_data)):
                if check_ip(review_data[i]['uid']) == False:
                    registered.append(review_data[i]['uid']) 
            if loggedIn:
                userUid = session['user']
            else:
                userUid = None
            return render_template('jabol_page.html', jabol_data=data[f"{id}"], id=id, review_data=review_data, isChild=True, site_key=SECRETS['site_key'], loggedIn=loggedIn, admins=admins, pro=pro, uid=userUid, registered=registered)
        elif request.method == "POST":
            # response = request.form['g-recaptcha-response']
            # verify_response = requests.post(url=f'{VERIFY_URL}?secret={SECRETS["secret_key"]}&response={response}')
            # if verify_response['success'] == False:
            #     abort(401)
            new_entry = {}
            new_entry["drink_id"] = id
            new_entry["review"] = request.form["review"]
            new_entry["date"] = datetime.now(tzinfo).strftime("%d.%m.%Y - %H:%M")
            new_entry["verified"] = False
            if "user" in session:
                userdat = get_user_data(users_file, session["user"])
                new_entry["name"] = userdat["username"]
                new_entry["uid"] = session["user"]
                reviews = readfile(review_file)
                for rev in reviews:
                    if reviews[rev]['uid'] == session['user'] and reviews[rev]['drink_id'] == id:
                        flash("Już dodałeś recenzję do tego jabola!")
                        return redirect(f"/archive/{id}")
            else:
                new_entry["name"] = "Anonimowy użytkownik"
                new_entry["uid"] = str(request.headers['x-real-ip'])
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
    if "user" in session:
        loggedIn = True
    else:
        loggedIn = False
    with open(file, "r") as f:
        database = json.load(f)
    if loggedIn:
        user_id = session['user']
    else:
        user_id = str(request.headers['x-real-ip'])
    score = int(request.form["score"])
    if score > 10 or score < 0:
        return f"<b>Ocena {score} wykracza poza ramy 0-10</b>"
    if user_id not in database[f"{id}"]["votes"]:
        database[f"{id}"]["votes"].append(user_id)
        database[f"{id}"]["scores"].append(score)
        database[f"{id}"]["score"] = sum(database[f"{id}"]["scores"]) / len(database[f"{id}"]["scores"])
        save_database(file, database)
        if loggedIn:
            add_points(session['user'], 15, users_file)
    else:
        flash("Już oceniałeś tego jabola!")
    return redirect(f"/archive/{id}")

@app.route("/submit", methods=["POST", "GET"])
def submit_suggestion():
    if request.method == "GET":
        if "user" in session:
            loggedIn = True
        else:
            loggedIn = False
        return render_template('submit.html', submitted=False, site_key=SECRETS['site_key'], loggedIn=loggedIn)
    elif request.method == "POST":
        db = readfile(file)
        new_entry = {}
        if 'user' in session:
            user_id = session['user']
        else:
            user_id = str(request.headers['x-real-ip'])
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
        if request.form["not-in-sale"] == False:
            new_entry["shops"] = request.form["shops"]
        else:
            new_entry["shops"] = "Wycofany ze sprzedaży."
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

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        if "user" in session:
            loggedIn = True
        else:
            loggedIn = False
        return render_template("register.html", site_key=SECRETS['site_key'], loggedIn=loggedIn)
    elif request.method == "POST":
        # response = request.form['g-recaptcha-response']
        # verify_response = requests.post(url=f'{VERIFY_URL}?secret={SECRETS["secret_key"]}&response={response}')
        # if verify_response['success'] == False:
        #     abort(401)

        users = readfile(users_file)
        usernames = []
        for i in users:
            usernames.append(users[f'{i}']["username"])
        if request.form["password"] == request.form["rpassword"]:
            new_user = {}
            new_user["username"] = request.form["username"]
            new_user["password"] = hash_password(request.form["password"])
            new_user["date_created"] = datetime.now(tzinfo).strftime("%d.%m.%Y - %H:%M")
            new_user["last_login"] = new_user["date_created"]
            new_user["points"] = 0
            new_user["pro"] = False
            new_user["admin"] = False
            if new_user["username"] not in usernames:
                appendfile(users_file, new_user)
                flash("Pomyślnie utworzono konto!")
                return redirect('/register')
            else:
                flash("Użytkownik o takiej nazwie już istnieje!")
                return redirect('/register')
        else:
            flash("Hasła muszą być takie same.")
            return redirect('/register')

@app.route("/login", methods=["POST", "GET"])
def login():
    if "user" in session:
        loggedIn = True
    else:
        loggedIn = False
    if request.method == "GET":
        return render_template("login.html", site_key=SECRETS['site_key'], loggedIn=loggedIn, user_colors=user_colors)
    elif request.method == "POST":
        users = readfile(users_file)
        found = False
        for i in users:
            if users[f'{i}']["username"] == request.form["username"]:
                found = True
                user = users[f'{i}']
                uid = i
        if found:
            if check_password(request.form["password"], user["password"]):
                edit_database(uid, "last_login", datetime.now(tzinfo).strftime("%d.%m.%Y - %H:%M"), users_file)
                session.permanent = True
                session["user"] = uid
                flash("Zalogowano pomyślnie!")
                return redirect("/")
            else:
                flash("Wprowadzone dane są nieprawidłowe.")
                return render_template("login.html", site_key=SECRETS['site_key'], loggedIn=loggedIn)
        else:
            flash("Wprowadzone dane są nieprawidłowe.")
            return render_template("login.html", site_key=SECRETS['site_key'], loggedIn=loggedIn)
        
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Zostałeś/aś wylogowany/a!")
    return redirect("/")

@app.route("/profile")
def profile():
    if "user" in session:
        loggedIn = True
    else:
        loggedIn = False
        return redirect("/login")
    userdata = get_user_data(users_file, session["user"])
    return render_template("profile.html", loggedIn=loggedIn, userdata=userdata)

@app.route("/profile/<uid>")
def viewProfile(uid):
    if "user" in session:
        loggedIn = True
    else:
        loggedIn = False
    userdata = get_user_data(users_file, uid)
    return render_template("profile.html", loggedIn=loggedIn, userdata=userdata, isChild = True)

@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route("/discord")
def discord():
    return redirect(CONFIG["discord_link"])

@app.route("/remove-review/<id>")
def remove_review(id):
    if 'user' not in session:
        redirect('/')
    else:
        uid = session['user']
        reviews = readfile(review_file)
        if reviews[f"{id}"]['uid'] == uid:
            x = id
            removeentry(review_file, x)
            add_points(uid, -50, users_file)
        return redirect(f"/archive")

@app.route("/admin")
def admin():
    if 'user' not in session:
        return FORBIDDEN, 403
    uid = session['user']
    udata = get_user_data(users_file, uid)
    if udata['admin'] == False:
        return FORBIDDEN, 403
    else:
        r = readfile(review_file)
        reviews = []
        for i in r:
            if r[i]['verified'] == False:
                r[i]['idx'] = i
                reviews.append(r[i])
        j = readfile(file)
        jabole = []
        for i in j:
            if j[i]['verified'] == False:
                j[i]['idx'] = i
                jabole.append(j[i])
                print(j)
        return render_template('admin.html', loggedIn=True, reviews=reviews, jabole=jabole)

@app.route("/admin/acceptR/<id>", methods=["GET"])
def admin_acceptR(id):
    if 'user' not in session:
        return FORBIDDEN, 403
    uid = session['user']
    udata = get_user_data(users_file, uid)
    if udata['admin'] == False:
        return FORBIDDEN, 403
    else:
        edit_database(id, 'verified', True, review_file)
        flash("Zaakceptowano recenzje!")
        return redirect("/admin")

@app.route("/admin/accept/<id>", methods=["GET"])
def admin_accept(id):
    if 'user' not in session:
        return FORBIDDEN, 403
    uid = session['user']
    udata = get_user_data(users_file, uid)
    if udata['admin'] == False:
        return FORBIDDEN, 403
    else:
        edit_database(id, 'verified', True, file)
        flash("Zaakceptowano jabola!")
        return redirect("/admin")

@app.route("/admin/removeR/<id>", methods=["GET"])
def admin_removeR(id):
    if 'user' not in session:
        return FORBIDDEN, 403
    uid = session['user']
    udata = get_user_data(users_file, uid)
    if udata['admin'] == False:
        return FORBIDDEN, 403
    else:
        removeentry(review_file, id)
        flash("Odrzucono recenzje!")
        return redirect("/admin")

@app.route("/admin/remove/<id>", methods=["GET"])
def admin_remove(id):
    if 'user' not in session:
        return FORBIDDEN, 403
    uid = session['user']
    udata = get_user_data(users_file, uid)
    if udata['admin'] == False:
        return FORBIDDEN, 403
    else:
        removeentry(file, id)
        flash("Odrzucono jabola!")
        return redirect("/admin")



if __name__ == '__main__':
    app.run(debug=True)