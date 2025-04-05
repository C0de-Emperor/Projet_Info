from flask import Flask, render_template, request, redirect, url_for
from pythonScripts import loginManager as lg
from pythonScripts import dbManager as dbm

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('login.html')


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
    if request.method == 'POST':
        sport = request.form.get('sport')
        matchDuration = request.form.get('matchDuration')
        teamSize = request.form.get('teamSize')
        availableSportsFields = request.form.get('availableSportsFields')
        algorithm = request.form.get('algorithm')
        maxTeamNumber = request.form.get('maxTeamNumber')
        teamSelectionMethod = request.form.get('teamSelectionMethod')
        points = request.form.get('points')
        tournamentId = request.form.get('tournamentId')
        password = request.form.get('password')

        if sport == "" :
            return render_template('create.html', error="Sport is empty")
        if matchDuration == "" :
            return render_template('create.html', error="Match Duration is empty")
        if teamSize == "" :
            return render_template('create.html', error="Team Size is empty")
        if availableSportsFields == "" :
            return render_template('create.html', error="Available Sports Fields is empty")
        if algorithm == "" :
            return render_template('create.html', error="Algorithm is empty")
        if maxTeamNumber == "" :
            return render_template('create.html', error="Max Team Number is empty")
        if teamSelectionMethod == "" :
            return render_template('create.html', error="Team Selection Method is empty")
        if points == "" :
            return render_template('create.html', error="Points Sports Fields is empty")
        if tournamentId == "" :
            return render_template('create.html', error="Tournament Id is empty")
        if password == "" :
            return render_template('create.html', error="Password is empty")
        
        try:
            int(matchDuration)
            int(teamSize)
            int(availableSportsFields)
            int(maxTeamNumber)
        except:
            return render_template('create.html', error="Invalid data type")

        if not lg.IsUniqueId(tournamentId):
            return render_template('create.html', error="Id already taken")

        #if ... in

        lg.AddNewLogin(tournamentId, password)

        #perform databasecreation

    return render_template('create.html')

if __name__ == '__main__':
    app.run(debug=True)