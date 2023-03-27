from flask import Flask

app = Flask(__name__)

@app.route('/')
def main():
    return app.send_static_file('index.html')

@app.route('/archive')
def archive():
    return app.send_static_file('archive.html')

@app.route('/archive/<id>')
def id(id):
    return f'Page of id: {id}'

if(__name__ == '__main__'):
    app.run(debug=True)