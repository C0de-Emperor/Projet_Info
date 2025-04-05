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

            return render_template("/createTournament", isCreating=False)
        else:
            return render_template('orgaLogin.html', parametersList=lg.getParamatersList(databaseId), error="Identifiants invalides.")
    return render_template('orgaLogin.html')


@app.route('/createTournament', methods=['GET', 'POST'])
def create():
    tournamentList = []
    if request.method == 'POST':
        tournamentDict = {}
        inputsNameList = ["sport", "matchDuration", "teamSize", "availableSportFields", "algorithm", "maxTeamNumber", "teamSelectionMethod", "points"]

        for k in inputsNameList:
            tournamentDict[k] = request.form.get(k)
            tournamentList.append(request.form.get(k))
        tournamentId = request.form.get("tournamentId")
        password = request.form.get("password")

        print(tournamentList)

        for (key, value) in tournamentDict.items():
            if value == "":
                return render_template("createTournament.html", error=key+" is empty", parametersList=tournamentList, isCreating=True)
        
        try:
            int(tournamentDict["matchDuration"])
            int(tournamentDict["teamSize"])
            int(tournamentDict["availableSportsField"])
            int(tournamentDict["maxTeamNumber"])
        except:
            return render_template('createTournament.html', error="Invalid data type", parametersList=tournamentList, isCreating=True)

        if not lg.IsUniqueId(tournamentId):
            return render_template('createTournament.html', error="Id already taken", parametersList=tournamentList, isCreating=True)

        #if ... in

        lg.AddNewLogin(tournamentId, password)
        dbm.createTournament(tournamentId, tournamentDict)
        
    return render_template('createTournament.html', parametersList=tournamentList, isCreating=True)

if __name__ == '__main__':
    app.run(debug=True)