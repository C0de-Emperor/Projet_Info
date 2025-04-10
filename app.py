from flask import Flask, render_template, request, redirect, url_for
from pythonScripts import loginManager as lm
from pythonScripts import dbManager as dbm

app = Flask(__name__)


@app.route('/')
def Index():
    return render_template('index.html')


@app.route('/orgaLogin', methods=['GET', 'POST'])
def OrgaLogin():
    if request.method == 'POST':
        tournamentName = request.form.get('tournamentName', '').strip()
        password = request.form.get('password', '').strip()

        # 🛑 Champs vides
        if not tournamentName:
            return render_template('orgaLogin.html', error="Tournament name is empty")

        if not password:
            return render_template('orgaLogin.html', error="Password is empty")

        # ✅ Identifiants corrects
        if lm.IsLoginCorrect(tournamentName, password):
            parametersList = lm.GetParamatersList(tournamentName)
            return render_template("createTournament.html", parametersList=parametersList, isCreating=False)

        # ❌ Échec login
        return render_template('orgaLogin.html', error="Invalid credentials")

    # GET method
    return render_template('orgaLogin.html')


@app.route('/createTournament', methods=['GET', 'POST'])
def CreateTournament():
    tournamentList = []
    creatingState = True

    if request.method == 'POST':
        tournamentDict = {}
        inputNames = [
            "sport", "matchDuration", "teamSize", "availableSportFields",
            "algorithm", "maxTeamNumber", "teamSelectionMethod", "points", "refereePassword"
        ]

        for key in inputNames:
            value = request.form.get(key, "").strip()
            tournamentDict[key] = value
            tournamentList.append(value)

        tournamentName = request.form.get("tournamentName", "").strip()
        password = request.form.get("password", "").strip()

        tournamentList.append(tournamentName)
        tournamentList.append(password)

        # Check si c'est une modification (pas de mot de passe) ou une création
        if password == None:
            creatingState = False

        # 🛑 Nom invalide
        if " " in tournamentName or tournamentName == "":
            return render_template(
                'createTournament.html',
                error="The tournament name must not contain spaces or be empty.",
                parametersList=tournamentList,
                isCreating=creatingState
            )

        # 🛑 Champs vides
        for key, value in tournamentDict.items():
            if value == "":
                return render_template(
                    "createTournament.html",
                    error=f"{key} is empty",
                    parametersList=tournamentList,
                    isCreating=creatingState
                )

        # 🛑 Vérif type numérique
        try:
            int(tournamentDict["matchDuration"])
            int(tournamentDict["teamSize"])
            int(tournamentDict["availableSportFields"])
            int(tournamentDict["maxTeamNumber"])
        except ValueError:
            return render_template(
                'createTournament.html',
                error="Invalid data type: matchDuration, teamSize, availableSportFields, and maxTeamNumber must be integers.",
                parametersList=tournamentList,
                isCreating=creatingState
            )

        # ✔️ MODIFICATION
        if password == None:
            dbm.WriteTournamentParameters(tournamentName, tournamentDict)
            return render_template("orgaLogin.html", error="Tournament successfully modified")

        # 🛑 ID déjà pris
        if not lm.IsUniqueId(tournamentName):
            return render_template(
                'createTournament.html',
                error="Tournament name is already taken.",
                parametersList=tournamentList,
                isCreating=creatingState
            )

        # ✔️ CRÉATION
        lm.AddNewLogin(tournamentName, password)
        dbm.CreateTournament(tournamentName, tournamentDict)

        return render_template("orgaLogin.html", error="Tournament successfully created")

    # GET
    return render_template('createTournament.html', parametersList=tournamentList, isCreating=creatingState)


@app.route('/createTeam', methods=['GET', 'POST'])
def CreateTeam():
    teamList = []
    teamMembers = []
    n = 0
    creatingState = True

    if request.method == 'POST':
        # Récupération des valeurs principales
        teamDict = {
            "tournamentName": request.form.get("tournamentName", "").strip(),
            "teamName": request.form.get("teamName", "").strip(),
            "password": request.form.get("password", "").strip() or None
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
            first_name = request.form.get(f"teamMemberFirstName{i}", "").strip()
            last_name = request.form.get(f"teamMemberLastName{i}", "").strip()
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
            return render_template("chiefTeamLogin.html", error="Team successfully created", parametersList=[])

        # Mise à jour d’équipe
        else:
            if lm.IsUniqueTeamId(teamDict["teamName"], teamDict["tournamentName"]):
                return render_template("createTeam.html", error="Team Name Doesn't Exist", n=n, parametersList=teamList, teamMembers=teamMembers, isCreating=creatingState)

            dbm.UpdateTeam(teamDict["tournamentName"], teamDict["teamName"], teamMembers)
            return render_template("chiefTeamLogin.html", error="Team successfully updated", parametersList=[])

    # GET request
    return render_template("createTeam.html", isCreating=creatingState, n=n, teamMembers=teamMembers, parametersList=teamList)


@app.route('/chiefTeamLogin', methods=['GET', 'POST'])
def ChiefTeamLogin():
    teamList = []
    
    if request.method == 'POST':
        # Récupération des champs
        teamDict = {
            "tournamentName": request.form.get("tournamentName", "").strip(),
            "teamName": request.form.get("teamName", "").strip(),
            "password": request.form.get("password", "").strip()
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
        dbPath = f"databases/tournament{teamDict['tournamentName']}Database.db"
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
    if request.method == 'POST':
        tournamentName = request.form.get("tournamentName", "").strip()
        refereePassword = request.form.get("refereePassword", "").strip()

        # Validation des champs
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
        return render_template("referee.html", parametersList=[tournamentName], matchesList=currentMatchesList)

    # GET request
    return render_template("refereeLogin.html")


@app.route("/referee", methods=["GET", "POST"])
def Referee():
    if request.method == "POST":
        tournamentName = request.form.get("tournamentName")
        matchId = request.form.get("matchButton")
        submit_point = request.form.get("submitPoint")

        # Redirige si un score est soumis
        if submit_point == "1":
            playerId = request.form.get("playerId", "").strip()
            pointsScored = request.form.get("pointsScored", "").strip()
            hasTeam1Scored = request.form.get("hasTeam1Scored")
            hasTeam2Scored = request.form.get("hasTeam2Scored")

            # Vérification des champs obligatoires
            if not playerId or not pointsScored:
                error_field = "playerId" if not playerId else "pointsScored"
                return render_template(
                    "referee.html",
                    error=f"{error_field} is empty",
                    matchInfos=dbm.GetMatch(tournamentName, matchId),
                    parametersList=[tournamentName, matchId]
                )

            if hasTeam1Scored == hasTeam2Scored:
                return render_template(
                    "referee.html",
                    error="Both teams can't have the same outcome",
                    matchInfos=dbm.GetMatch(tournamentName, matchId),
                    parametersList=[tournamentName, matchId]
                )

            result = dbm.AddPoint(
                tournamentName,
                matchId,
                playerId,
                pointsScored,
                hasTeam1Scored == "on"
            )

            if result:
                print("AddPoint returned:", result)

            # Redirection en GET avec les bons paramètres
            return redirect(url_for("Referee", getMethodTournamentName=tournamentName, getMethodMatchId=matchId))

        # Sinon, juste afficher le match sélectionné
        return render_template(
            "referee.html",
            matchInfos=dbm.GetMatch(tournamentName, matchId),
            parametersList=[tournamentName, matchId]
        )

    # Gestion GET
    elif request.method == "GET":
        tournamentName = request.args.get("getMethodTournamentName")
        matchId = request.args.get("getMethodMatchId")

        if not tournamentName or not matchId:
            return render_template("referee.html", error="Missing parameters")

        return render_template(
            "referee.html",
            matchInfos=dbm.GetMatch(tournamentName, matchId),
            parametersList=[tournamentName, matchId]
        )

    return render_template("referee.html")


@app.route("/spectatorLogin", methods=["GET", "POST"])
def spectatorLogin():
    if request.method == "POST":
        tournamentName=request.form.get("tournamentName")
        if lm.IsExistingTournament(tournamentName):
            return render_template("spectator.html", parametersList=[tournamentName], matchesList=dbm.GetMatches(tournamentName))
        else:
            return render_template("spectatorLogin.html", error="unvalid tournament name")
    return render_template("spectatorLogin.html")


@app.route("/spectator", methods=["GET", "POST"])
def Spectator():
    spectatorList=[]
    if request.method == "POST":
        spectatorList.append(request.form.get("tournamentName"))
        spectatorList.append(request.form.get("matchButton"))

        print(request.form.get("tournamentName"))
        
        return render_template("spectator.html", parametersList=spectatorList, points=dbm.GetPoints(spectatorList[0], spectatorList[1]))
    return render_template("spectator.html")


if __name__ == '__main__':
    app.run(debug=True)