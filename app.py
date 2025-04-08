from flask import Flask, render_template, request
from pythonScripts import loginManager as lg
from pythonScripts import dbManager as dbm

app = Flask(__name__)


@app.route('/')
def Index():
    return render_template('index.html')


@app.route('/orgaLogin', methods=['GET', 'POST'])
def OrgaLogin():
    if request.method == 'POST':
        databaseId = request.form.get('tournamentName')
        password = request.form.get('password')

        if databaseId == "" :
            return render_template('orgaLogin.html', error="Database Id is empty")
        if password == "" :
            return render_template('orgaLogin.html', error="Password is empty")

        if lg.IsLoginCorrect(databaseId, password):
            return render_template("createTournament.html", parametersList=lg.GetParamatersList(databaseId), isCreating=False)
        else:
            return render_template('orgaLogin.html', error="Identifiants invalides.")
    return render_template('orgaLogin.html')


@app.route('/createTournament', methods=['GET', 'POST'])
def CreateTournament():
    tournamentList = []
    if request.method == 'POST':
        tournamentDict = {}
        inputsNameList = ["sport", "matchDuration", "teamSize", "availableSportFields", "algorithm", "maxTeamNumber", "teamSelectionMethod", "points", "refereePassword"]

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

        #if ... in

        if password==None:
            dbm.WriteTournamentParameters(tournamentName, tournamentDict)
            return render_template("orgaLogin.html", error="Tournament successfully modified")

        if not lg.IsUniqueId(tournamentName):
            return render_template('createTournament.html', error="Id already taken", parametersList=tournamentList, isCreating=True)   #log    


        lg.AddNewLogin(tournamentName, password)
        dbm.CreateTournament(tournamentName, tournamentDict)

        return render_template("orgaLogin.html", error="Tournament successfully created")
        
    return render_template('createTournament.html', parametersList=tournamentList, isCreating=True)


@app.route('/createTeam', methods=['GET', 'POST'])
def CreateTeam ():
    return render_template("createTeam.html")


@app.route('/chiefTeamLogin', methods=['GET', 'POST'])
def ChiefTeamLogin ():
    teamList = []
    if request.method == 'POST':
        teamDict = {}
        inputsList = ["tournamentName", "teamName", "password"]

        for k in inputsList:
            teamDict[k] = request.form.get(k)
            teamList.append(request.form.get(k))
            
        for (key, value) in teamDict.items():
            if value == "":
                return render_template("chiefTeamLogin.html", error= key + " is empty", parametersList=teamList)

        if not lg.IsExistingTournament(teamDict["tournamentName"]):
            return render_template("chiefTeamLogin.html", error= "Invalid Tournament Name", parametersList=teamList)

        dbPath = "databases/tournament" + teamDict["refereePassword"] + "Database.db"
        if not dbm.IsTeamLoginCorrect(dbPath, teamDict["teamName"], teamDict["password"]):
            render_template("chiefTeamLogin.html", error= "Invalid Password", parametersList=teamList)

        #######

    return render_template("chiefTeamLogin.html", parametersList=teamList)


@app.route('/refereeLogin', methods=['GET', 'POST'])
def RefereeLogin ():
    refereeList = []
    if request.method == 'POST':
        refereeDict = {}
        inputsList = ["tournamentName", "refereePassword"]

        for k in inputsList:
            refereeDict[k] = request.form.get(k)
            refereeList.append(request.form.get(k))
            
        for (key, value) in refereeDict.items():
            if value == "":
                return render_template("refereeLogin.html", error= key + " is empty", parametersList=refereeList)

        if lg.GetParamatersList(refereeDict["tournamentName"])[8] == refereeDict["refereePassword"]:
            currentMatchesList = dbm.GetMatches(refereeDict["tournamentName"])
            return render_template("referee.html", tournamentName=refereeDict["tournamentName"], matchesList=currentMatchesList)

    return render_template("refereeLogin.html", parametersList=refereeList)

@app.route("/referee", methods=["GET", "POST"])
def Referee():
    refereeList=[]
    if request.method== "POST":
        refereeDict = {}
        inputsList = ["tournamentName", "refereePassword"]

        for k in inputsList:
            refereeDict[k] = request.form.get(k)
            refereeList.append(request.form.get(k))

    return render_template("referee.html")


if __name__ == '__main__':
    app.run(debug=True)