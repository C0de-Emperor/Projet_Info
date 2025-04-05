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
        databaseId = request.form.get('tournamentName')
        password = request.form.get('password')

        if databaseId == "" :
            return render_template('orgaLogin.html', error="Database Id is empty")
        if password == "" :
            return render_template('orgaLogin.html', error="Password is empty")

        if lg.IsLoginCorrect(databaseId, password):
            return render_template("createTournament.html", parametersList=lg.getParamatersList(databaseId), isCreating=False)
        else:
            return render_template('orgaLogin.html', error="Identifiants invalides.")
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
        tournamentName = request.form.get("tournamentName")
        password = request.form.get("password")
        tournamentList.append(tournamentName)
        tournamentList.append(password)

        if " " in tournamentName:
            return render_template('createTournament.html', error="The tournament's name musnt have spaces in it", parametersList=tournamentList, isCreating=True)

        for (key, value) in tournamentDict.items():
            if value == "":
                return render_template("createTournament.html", error=key+" is empty", parametersList=tournamentList, isCreating=True)
        
        try:
            int(tournamentDict["matchDuration"])
            int(tournamentDict["teamSize"])
            int(tournamentDict["availableSportFields"])
            int(tournamentDict["maxTeamNumber"])
        except:
            return render_template('createTournament.html', error="Invalid data type", parametersList=tournamentList, isCreating=True)

        if password==None:
            dbm.writeTournamentParameters(tournamentName, tournamentDict)
            return render_template("orgaLogin.html", error="Tournament successfully modified")

        if not lg.IsUniqueId(tournamentName):
            return render_template('createTournament.html', error="Id already taken", parametersList=tournamentList, isCreating=True)

        #if ... in

        lg.AddNewLogin(tournamentName, password)
        dbm.createTournament(tournamentName, tournamentDict)

        return render_template("orgaLogin.html", error="Tournament successfully created")
        
    return render_template('createTournament.html', parametersList=tournamentList, isCreating=True)

if __name__ == '__main__':
    app.run(debug=True)