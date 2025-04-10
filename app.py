from flask import Flask, render_template, request, redirect, url_for
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
def CreateTeam():
    teamList = []
    teamMembers = []
    n = 0

    creatingState = True

    if request.method == 'POST':
        action = request.form.get("verify")
        teamDict = {}
        inputsList = ["tournamentName", "teamName", "password"]

        for k in inputsList:
            teamDict[k] = request.form.get(k)
            teamList.append(request.form.get(k))

        if teamDict["password"] == None:
            creatingState = False
            del teamDict["password"]
            del teamList[2]
            del inputsList[2]

        if teamList[0] == "":
            return render_template("createTeam.html", error="Tournament name is empty", n=n, parametersList=teamList, teamMembers=teamMembers, isCreating=creatingState)

        if not lg.IsExistingTournament(teamList[0]):
            return render_template("createTeam.html", error="Invalid Tournament Name", n=n, parametersList=teamList, teamMembers=teamMembers, isCreating=creatingState)

        try:
            n = int(lg.GetParamatersList(teamList[0])[2])
        except:
            return render_template("createTeam.html", error="Erreur en récupérant la taille d'équipe", n=n, parametersList=teamList, teamMembers=teamMembers, isCreating=creatingState)

        for i in range(n):  # maintenant i de 0 à n-1
            member = [request.form.get(f"teamMemberFirstName{i}"), request.form.get(f"teamMemberLastName{i}")]
            teamMembers.append(member)

        if action == "verify" and creatingState:
            return render_template("createTeam.html", parametersList=teamList, n=n, teamMembers=[["", ""]] * n, isCreating=creatingState)

        for value in teamDict.values():
            if value == "":
                return render_template("createTeam.html", error="One of the inputs is empty", n=n, parametersList=teamList, teamMembers=teamMembers, isCreating=creatingState)

        for member in teamMembers:
            if member[0] == "" or member[1] == "":
                return render_template("createTeam.html", error="A member is empty", n=n, parametersList=teamList, teamMembers=teamMembers, isCreating=creatingState)

        if creatingState:
            if not lg.IsUniqueTeamId(teamList[1], teamList[0]):
                return render_template("createTeam.html", error="Team Name Already Exists", n=n, parametersList=teamList, teamMembers=teamMembers, isCreating=creatingState)
            
            dbm.AddTeam(teamList[0], teamList[1], teamMembers, 0, teamList[2])
            return render_template("chiefTeamLogin.html", error="Team successfully created", parametersList=[])
        
        else:
            if lg.IsUniqueTeamId(teamList[1], teamList[0]):
                return render_template("createTeam.html", error="Team Name Doesn't Exists", n=n, parametersList=teamList, teamMembers=teamMembers, isCreating=creatingState)
            
            #dbm.AddTeam(teamList[0], teamList[1], teamMembers, 0, teamList[2])
            return render_template("chiefTeamLogin.html", error="Team successfully updated", parametersList=[])

    return render_template("createTeam.html", isCreating=creatingState, n=n, teamMembers=teamMembers, parametersList=teamList)


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

        dbPath = "databases/tournament" + teamDict["tournamentName"] + "Database.db"
        if not dbm.IsTeamLoginCorrect(dbPath, teamDict["teamName"], teamDict["password"]):
            render_template("chiefTeamLogin.html", error= "Invalid Password", parametersList=teamList)

        teamMembers = [[member[1], member[2]] for member in dbm.GetTeamPlayers(teamList[0], teamList[1])]
        return render_template("createTeam.html", parametersList=teamList, n=len(teamMembers), teamMembers=teamMembers, isCreating=False)

    return render_template("chiefTeamLogin.html", parametersList=teamList)


@app.route('/refereeLogin', methods=['GET', 'POST'])
def RefereeLogin ():
    if request.method == 'POST':
        refereeDict = {}
        tournamentName=request.form.get("tournamentName")
        refereePassword=request.form.get("refereePassword")
            
        if tournamentName == "":
            return render_template("refereeLogin.html", error= "tournamentName is empty")
        if refereePassword == "":
            return render_template("refereeLogin.html", error= "refereePassword is empty", tournamentName=tournamentName)

        if lg.GetParamatersList(tournamentName)[8] == refereePassword:
            currentMatchesList = dbm.GetMatches(tournamentName)
            return render_template("referee.html", parametersList=[tournamentName], matchesList=currentMatchesList)

    return render_template("refereeLogin.html")


@app.route("/referee", methods=["GET", "POST"])
def Referee():
    refereeList=[]
    if request.method== "POST":
        refereeList.append(request.form.get("tournamentName"))
        refereeList.append(request.form.get("matchButton"))

        if request.form.get("submitPoint")=="1":
            inputsList = ["playerId", "pointsScored", "hasTeam1Scored", "hasTeam2Scored"]
            print('MAI BORDEL', refereeList)

            for k in inputsList:
                refereeList.append(request.form.get(k))

            print("PUTAAAIN", refereeList)
            
            for k in range(2,4):
                if refereeList[k]=="": return render_template("referee.html", error=inputsList[k-2]+" is empty" , matchInfos=dbm.GetMatch(refereeList[0], refereeList[1]), parametersList=refereeList)
            if refereeList[4]==refereeList[5]: return render_template("referee.html", error="Both teams cant have the same outcome" , matchInfos=dbm.GetMatch(refereeList[0], refereeList[1]), parametersList=refereeList)

            returnValue=dbm.AddPoint(refereeList[0], refereeList[1], refereeList[2], refereeList[3], refereeList[4]=="on")
            if returnValue!="": print(returnValue)

            print("koloui")
            return redirect(url_for("Referee", getMethodTournamentName=refereeList[0], getMethodMatchId=refereeList[1]))
        else:
            return render_template("referee.html", matchInfos=dbm.GetMatch(refereeList[0], refereeList[1]), parametersList=refereeList)
    elif request.method=="GET":
        getMethodTournamentName=request.args.get("getMethodTournamentName")
        getMethodMatchId=request.args.get("getMethodMatchId")
        return render_template("referee.html", matchInfos=dbm.GetMatch(getMethodTournamentName, getMethodMatchId), parametersList=[getMethodTournamentName, getMethodMatchId])
    
    return render_template("referee.html")

if __name__ == '__main__':
    app.run(debug=True)