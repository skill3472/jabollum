from flask import Flask, render_template
import json
import os

app = Flask(__name__, template_folder='static')

file = "db/db.json"

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
    return render_template('archive.html', table_data=data)

@app.route('/archive/<id>')
def id(id):
    return f'Page of id: {id}'

if(__name__ == '__main__'):
    app.run(debug=True)