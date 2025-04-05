from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('databaseId')
        password = request.form.get('password')
        if username == "admin" and password == "secret":
            return "vous êtes connecté"
            #return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Identifiants invalides.")
    return render_template('login.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    return render_template('create.html')

if __name__ == '__main__':
    app.run(debug=True)