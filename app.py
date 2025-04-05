from flask import Flask, render_template, request, redirect, url_for
from pythonScripts import loginManager as lg

app = Flask(__name__)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        databaseId = request.form.get('databaseId')
        password = request.form.get('password')

        if databaseId == "" :
            return render_template('login.html', error="Database Id is empty")
        if password == "" :
            return render_template('login.html', error="Password is empty")

        if lg.IsLoginCorrect(databaseId, password):
            return "Vous êtes connecté"
            #return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Identifiants invalides.")
    return render_template('login.html')


@app.route('/create', methods=['GET', 'POST'])
def create():
    return render_template('create.html')

if __name__ == '__main__':
    app.run(debug=True)