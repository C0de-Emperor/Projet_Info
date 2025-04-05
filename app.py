from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)



@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == "admin" and password == "secret":
            return redirect(url_for('dashboard'))
        else:
            return render_template('index.html', error="Identifiants invalides.")
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return "Bienvenue dans le tableau de bord ! 🎉"

if __name__ == '__main__':
    app.run(debug=True)