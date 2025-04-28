from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from pythonScripts import loginManager as lm
from pythonScripts import dbManager as dbm

app = Flask(__name__)


@app.route('/')
def Index():
    return render_template('index.html')


@app.route('/orgaLogin', methods=['GET', 'POST'])
def OrgaLogin():
    tournamentList = []
    tournamentDict = {}
    if request.method == 'POST':
        inputNames = [
            "password", "tournamentName"
        ]

        for key in inputNames:
            value = request.form.get(key)
            tournamentDict[key] = value
            tournamentList.append(value)

        # Champs vides
        if tournamentDict["tournamentName"] == "":
            return render_template('orgaLogin.html', error="Tournament name is empty", parametersList=tournamentList)

        if tournamentDict["password"] == "":
            return render_template('orgaLogin.html', error="Password is empty", parametersList=tournamentList)

        # Identifiants corrects
        if lm.IsLoginCorrect(tournamentDict["tournamentName"], tournamentDict["password"]):
            parametersList = lm.GetParamatersList(tournamentDict["tournamentName"])
            return render_template("createTournament.html", parametersList=parametersList, isCreating=False, isStarted=parametersList[10])

        # Échec login
        return render_template('orgaLogin.html', error="Invalid credentials", parametersList=tournamentList)

    # POST method
    return render_template('orgaLogin.html')


@app.route('/createTournament', methods=['GET', 'POST'])
def CreateTournament():
    tournamentList=[]
    tournamentDict={}

    isCreating=request.args.get("isCreating") == "True"
    isStarted=request.args.get("isStarted") == "True"

    print(isCreating, isStarted)

    if request.method=="GET":
        return render_template("createTournament.html", parametersList=tournamentList, isCreating=isCreating, isStarted=isStarted)
    elif request.method=="POST":
        inputNames = ["sport", "matchDuration", "teamSize", "availableSportFields", "algorithm", "maxTeamNumber", "teamSelectionMethod", "points", "refereePassword", "password"]

        for key in inputNames:
            value = request.form.get(key)
            tournamentDict[key] = value
            tournamentList.append(value)
        
        # Champs vides ou non-authorisés
        for key, value in tournamentDict.items():
            if value == "":
                return render_template("createTournament.html",parametersList=tournamentList, isCreating=isCreating, isStarted=isStarted, error=f"{key} is empty",)
            if value!=None and dbm.separator in value:
                return render_template("createTournament.html", parametersList=tournamentList, isCreating=isCreating, isStarted=isStarted, error=f"{key} presents an unauthorized string : "+dbm.separator)

        # Vérif type numérique
        try:
            int(tournamentDict["matchDuration"])
            int(tournamentDict["teamSize"])
            int(tournamentDict["availableSportFields"])
            int(tournamentDict["maxTeamNumber"])
        except ValueError:
            return render_template(
                'createTournament.html', parametersList=tournamentList, isCreating=isCreating, isStarted=isStarted, error="Invalid data type: matchDuration, teamSize, availableSportFields, and maxTeamNumber must be integers.")

        if isCreating:
            tournamentDict["tournamentName"]=request.form.get("tournamentName")
            tournamentList.append(request.form.get("tournamentName"))

            # Nom invalide
            if " " in tournamentDict['tournamentName'] or tournamentDict['tournamentName'] == "":
                return render_template('createTournament.html', parametersList=tournamentList, isCreating=isCreating, isStarted=isStarted, error="The tournament name must not contain spaces or be empty.",)

            # ID déjà pris
            if isCreating and not lm.IsUniqueId(tournamentDict['tournamentName']):
                return render_template(
                    'createTournament.html', parametersList=tournamentList,isCreating=isCreating, error="Tournament name is already taken.")
            
            # CRÉATION
            dbm.CreateTournament(tournamentDict['tournamentName'], tournamentDict, isStarted)
            lm.AddNewLogin(tournamentDict['tournamentName'], tournamentDict['password'])

            return render_template("orgaLogin.html", validation="Tournament successfully created", parametersList=[])
        else:
            tournamentDict["tournamentName"] = request.args.get("tournamentName")
            tournamentList.append(request.args.get("tournamentName"))

            tournamentDict["isTournamentStarted"]=str(isStarted)

            if isStarted == True:
                return render_template(
                    'createTournament.html',
                    error="Tournament in progress cannot be modified.",
                    parametersList=tournamentList,
                    isCreating=isCreating,
                    isStarted=isStarted
                )
        
            # MODIFICATION
            action = request.form.get("action")
            if action == "startTournament":
                dbm.WriteTournamentParameters(tournamentDict, "True")
                return render_template("orgaLogin.html", validation="Tournament successfully started", parametersList=[])
            if action == "infrastructures":
                return redirect(url_for('Infrastructures', tournamentName=tournamentDict["tournamentName"], sportFieldNumber=tournamentDict["availableSportFields"]))
            else:
                dbm.WriteTournamentParameters(tournamentDict, "False")
                return render_template("orgaLogin.html", validation="Tournament successfully modified", parametersList=[])


@app.route('/createTeam', methods=['GET', 'POST'])
def CreateTeam():
    teamList = []
    teamMembers = []
    n = 0
    creatingState = True

    if request.method == 'POST':
        # Récupération des valeurs principales
        teamDict = {
            "tournamentName": request.form.get("tournamentName"),
            "teamName": request.form.get("teamName"),
            "password": request.form.get("password")
        }

        teamList = [teamDict["tournamentName"], teamDict["teamName"]]
        if teamDict["password"] is not None:
            teamList.append(teamDict["password"])
        else:
            creatingState = False

        # Vérification du nom de tournoi
        if not teamDict["tournamentName"]:
            return render_template("createTeam.html", error="Tournament name is empty", n=n, parametersList=teamList, teamMembers=teamMembers, isCreating=creatingState)

        if not lm.IsExistingTournament(teamDict["tournamentName"]):
            return render_template("createTeam.html", error="Invalid Tournament Name", n=n, parametersList=teamList, teamMembers=teamMembers, isCreating=creatingState)

        # Récupération du nombre de membres
        try:
            n = int(lm.GetParamatersList(teamDict["tournamentName"])[2])
        except Exception:
            return render_template("createTeam.html", error="Erreur en récupérant la taille d'équipe", n=n, parametersList=teamList, teamMembers=teamMembers, isCreating=creatingState)

        # Construction de la liste des membres
        for i in range(n):  # i de 0 à n-1
            first_name = request.form.get(f"teamMemberFirstName{i}")
            last_name = request.form.get(f"teamMemberLastName{i}")
            teamMembers.append([first_name, last_name])

        action = request.form.get("verify")

        # Vérification uniquement de la taille de l’équipe
        if action == "verify" and creatingState:
            return render_template("createTeam.html", parametersList=teamList, n=n, teamMembers=[["", ""]] * n, isCreating=creatingState)

        # Vérification des champs vides
        if any(not value for key, value in teamDict.items() if key != "password"):
            return render_template("createTeam.html", error="One of the inputs is empty", n=n, parametersList=teamList, teamMembers=teamMembers, isCreating=creatingState)

        if any(first == "" or last == "" for first, last in teamMembers):
            return render_template("createTeam.html", error="A member is empty", n=n, parametersList=teamList, teamMembers=teamMembers, isCreating=creatingState)

        # Création d’équipe
        if creatingState:
            if not lm.IsUniqueTeamId(teamDict["teamName"], teamDict["tournamentName"]):
                return render_template("createTeam.html", error="Team Name Already Exists", n=n, parametersList=teamList, teamMembers=teamMembers, isCreating=creatingState)

            dbm.AddTeam(teamDict["tournamentName"], teamDict["teamName"], teamMembers, 0, teamDict["password"])
            return render_template("chiefTeamLogin.html", validation="Team successfully created", parametersList=[])

        # Mise à jour d’équipe
        else:
            if lm.IsUniqueTeamId(teamDict["teamName"], teamDict["tournamentName"]):
                return render_template("createTeam.html", error="Team Name Doesn't Exist", n=n, parametersList=teamList, teamMembers=teamMembers, isCreating=creatingState)

            dbm.UpdateTeam(teamDict["tournamentName"], teamDict["teamName"], teamMembers)
            return render_template("chiefTeamLogin.html", validation="Team successfully updated", parametersList=[])

    # GET request
    return render_template("createTeam.html", isCreating=creatingState, n=n, teamMembers=teamMembers, parametersList=teamList)


@app.route('/infrastructures', methods=['GET', 'POST'])
def Infrastructures ():
    if request.method=="GET":
        return render_template("infrastructures.html", parametersList=[request.args.get("tournamentName"), int(request.args.get("sportFieldNumber"))])    


@app.route('/chiefTeamLogin', methods=['GET', 'POST'])
def ChiefTeamLogin():
    teamList = []
    
    if request.method == 'POST':
        # Récupération des champs
        teamDict = {
            "tournamentName": request.form.get("tournamentName"),
            "teamName": request.form.get("teamName"),
            "password": request.form.get("password")
        }
        teamList = list(teamDict.values())

        # Vérifie que tous les champs sont remplis
        for key, value in teamDict.items():
            if not value:
                return render_template("chiefTeamLogin.html", error=f"{key} is empty", parametersList=teamList)

        # Vérifie si le tournoi existe
        if not lm.IsExistingTournament(teamDict["tournamentName"]):
            return render_template("chiefTeamLogin.html", error="Invalid Tournament Name", parametersList=teamList)

        # Vérifie l'identité de l'équipe
        dbPath = f"databases/{teamDict['tournamentName']}.db"
        if not dbm.IsTeamLoginCorrect(dbPath, teamDict["teamName"], teamDict["password"]):
            return render_template("chiefTeamLogin.html", error="Invalid Password", parametersList=teamList)

        # Récupère les membres de l'équipe
        rawMembers = dbm.GetTeamPlayers(teamDict["tournamentName"], teamDict["teamName"])
        teamMembers = [[member[1], member[2]] for member in rawMembers]  # [firstName, lastName]

        return render_template("createTeam.html", parametersList=teamList, n=len(teamMembers), teamMembers=teamMembers, isCreating=False)

    # GET request
    return render_template("chiefTeamLogin.html", parametersList=teamList)


@app.route('/refereeLogin', methods=['GET', 'POST'])
def RefereeLogin():
    if request.method=="GET":
        return render_template("refereeLogin.html")
    elif request.method=="POST":
        tournamentName=request.form.get("tournamentName")
        refereePassword=request.form.get("refereePassword")

        return redirect(url_for("RefereeMatchChoice", tournamentName=tournamentName, refereePassword=refereePassword))


@app.route("/refereeMatchChoice", methods=["GET", "POST"])
def RefereeMatchChoice():
    tournamentName=request.args.get("tournamentName")
    refereePassword=request.args.get("refereePassword")
    if request.method=="GET":
        # Vérification des champs
        if not tournamentName:
            return render_template("refereeLogin.html", error="Tournament name is empty")
        if not refereePassword:
            return render_template("refereeLogin.html", error="Referee password is empty", tournamentName=tournamentName)
        
        # Vérification du mot de passe arbitre
        try:
            parameters = lm.GetParamatersList(tournamentName)
        except Exception as e:
            return render_template("refereeLogin.html", error="Tournament not found", tournamentName=tournamentName)
        
        if parameters[8] != refereePassword:
            return render_template("refereeLogin.html", error="Invalid referee password", tournamentName=tournamentName)
        
        # Si tout est bon
        currentMatchesList = dbm.GetMatches(tournamentName)
        return render_template("refereeMatchChoice.html", parametersList=[tournamentName, refereePassword], matchesList=currentMatchesList)
    
    elif request.method=="POST":
        matchId=request.form.get("matchIdButton")
        return redirect(url_for("Referee", tournamentName=tournamentName, refereePassword=refereePassword, matchId=matchId))


@app.route("/referee", methods=["GET", "POST"])
def Referee():
    tournamentName=request.args.get("tournamentName")
    refereePassword=request.args.get("refereePassword")
    matchId=request.args.get("matchId")
    if request.method=="POST":

        print(tournamentName, refereePassword, matchId)

        playerId = request.form.get("playerIdButton")
        pointsScored = request.form.get("pointsScored")

        result=dbm.AddPoint(tournamentName, matchId, playerId, pointsScored)

        if result!="": 
            print(result)
            return "<h1> MEH </h1>"
        
        matchTeams=[dbm.GetTeamPlayers(tournamentName, k) for k in dbm.GetMatch(tournamentName, matchId)[3:5]]
        return render_template("referee.html", parametersList=[tournamentName, refereePassword, matchId], matchInfos=dbm.GetMatch(tournamentName, matchId), teams=matchTeams, validation="point enregistré avec succès")
    elif request.method=="GET":
        matchTeams=[dbm.GetTeamPlayers(tournamentName, k) for k in dbm.GetMatch(tournamentName, matchId)[3:5]]
        return render_template("referee.html", parametersList=[tournamentName, refereePassword, matchId], matchInfos=dbm.GetMatch(tournamentName, matchId), teams=matchTeams)

    return render_template("referee.html", parametersList=[tournamentName, refereePassword, matchId], matchInfos=dbm.GetMatch(tournamentName, matchId))


@app.route("/spectatorLogin", methods=["GET", "POST"])
def SpectatorLogin():
    if request.method=="GET":
        return render_template("spectatorLogin.html")
    elif request.method == "POST":
        tournamentName=request.form.get("tournamentName")
        if lm.IsExistingTournament(tournamentName):
            return redirect(url_for("Spectator", tournamentName=tournamentName))
        else:
            return render_template("spectatorLogin.html")


@app.route("/spectator/<tournamentName>", methods=["GET", "POST"])
def Spectator(tournamentName):
    print(tournamentName)
    if request.method=="GET":
        return render_template("spectator.html", parametersList=[tournamentName], matchesList=dbm.GetMatches(tournamentName))
    elif request.method=="POST":
        matchId=request.form.get("matchIdButton")
        return render_template("spectator.html", parametersList=[tournamentName, matchId], points=dbm.GetPoints(tournamentName, matchId))
    

@app.route('/favicon.ico', methods=["GET"])
def Favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(debug=True)