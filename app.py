from flask import Flask, render_template, request, redirect, url_for
from pythonScripts import loginManager as lg
from pythonScripts import dbManager as dbm

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/orgaLogin', methods=['GET', 'POST'])
def orgaLogin():
    if request.method == 'POST':
        databaseId = request.form.get('databaseId')
        password = request.form.get('password')

        if databaseId == "" :
            return render_template('orgaLogin.html', error="Database Id is empty")
        if password == "" :
            return render_template('orgaLogin.html', error="Password is empty")

        if lg.IsLoginCorrect(databaseId, password):
            return "Vous êtes connecté"
            #return redirect(url_for('dashboard'))
        else:
            return render_template('orgaLogin.html', error="Identifiants invalides.")
    return render_template('orgaLogin.html')


@app.route('/createTournament', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        tournamentDict = {}
        inputsNameList = ["sport", "matchDuration", "teamSize", "availableSportFields", "algorithm", "maxTeamNumbber", "teamSelectionMethod", "points", "tournamentId", "password"]

        for k in inputsNameList:
            tournamentDict[k] = request.form.get(k)

        for (key, value) in tournamentDict:
            if value == "":
                return render_template("createTournament.html", error=key+" is empty")
        
        try:
            int(tournamentDict["matchDuration"])
            int(tournamentDict["teamSize"])
            int(tournamentDict["availableSportsField"])
            int(tournamentDict["maxTeamNumber"])
        except:
            return render_template('createTournament.html', error="Invalid data type")

        if not lg.IsUniqueId(tournamentDict["tournamentId"]):
            return render_template('createTournament.html', error="Id already taken")

        #if ... in

        lg.AddNewLogin(tournamentDict["tournamentId"], tournamentDict["password"])

        #perform databasecreation
    return render_template('createTournament.html')

if __name__ == '__main__':
    app.run(debug=True)