from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import jinja2.ext, os, sys
from pythonScripts import loginManager as lm
from pythonScripts import dbManager as dbm
from pythonScripts import configManager as cm
from pythonScripts import matchMakingManager as mmm

if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates'), static_folder=os.path.join(base_dir, 'static'))

# Cette solution a été trouvée sur internet afin de pouvoir compiler app.py avec la library cx_freeze et que flask continue à fonctionner (malgré le changement de dossier source)


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
            if value==None: value=""
            tournamentDict[key] = value
            tournamentList.append(value)

        # Champs vides
        if tournamentDict["tournamentName"] == "":
            return render_template('orgaLogin.html', error="Tournament name is empty", parametersList=tournamentList)

        if tournamentDict["password"] == "":
            return render_template('orgaLogin.html', error="Password is empty", parametersList=tournamentList)

        # Identifiants corrects
        if lm.IsLoginCorrect(tournamentDict["tournamentName"], tournamentDict["password"]):
            return redirect(url_for("CreateTournament", tournamentName=tournamentDict["tournamentName"], password=tournamentDict["password"], isCreating=False))

        # Échec login
        return render_template('orgaLogin.html', error="Invalid credentials", parametersList=tournamentList)

    # POST method
    return render_template('orgaLogin.html')


@app.route('/createTournament', methods=['GET', 'POST'])
def CreateTournament():
    tournamentList=[]
    tournamentDict={}

    tournamentName=request.args.get("tournamentName")
    isCreating=request.args.get("isCreating") == "True"

    if request.method=="GET":
        if isCreating:
            return render_template("createTournament.html", parametersList=tournamentList, isCreating=True, isStarted=False)
        else:
            tournamentList=lm.GetParamatersList(tournamentName)
            isStarted=tournamentList[8]
            tournamentList.append(request.args.get("password"))
            return render_template("createTournament.html", parametersList=tournamentList, isCreating=False, isStarted=isStarted)
    elif request.method=="POST":
        isStarted=False
        tournamentList=[]
        
        inputNames = ["sport", "matchDuration", "teamSize", "rankingMode", "maxTeamNumber", "points", "refereePassword", "password"]

        for key in inputNames:
            value = request.form.get(key)
            if value==None: value=""
            tournamentDict[key] = value
            tournamentList.append(value)
        
        if not isCreating: tournamentDict["password"]=" "
        
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
            int(tournamentDict["maxTeamNumber"])
        except ValueError:
            return render_template('createTournament.html', parametersList=tournamentList, isCreating=isCreating, isStarted=isStarted, error="Invalid data type: matchDuration, and maxTeamNumber must be integers.")

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
            isStarted=lm.GetParamatersList(tournamentName)[8]=="True"
            print(isStarted)
            del tournamentList[7]
            
            tournamentDict["tournamentName"] = request.args.get("tournamentName")
            tournamentList.append(request.args.get("tournamentName"))
            
            tournamentList.append("")
            tournamentDict["password"] = request.args.get("password")
            tournamentList.append(request.args.get("password"))

            tournamentDict["isTournamentStarted"]=str(isStarted)

            if isStarted == True:
                return render_template('createTournament.html', error="Tournament in progress cannot be modified.", parametersList=tournamentList, isCreating=isCreating, isStarted=isStarted)
            
            if not lm.IsLoginCorrect(tournamentDict["tournamentName"], tournamentDict["password"]):
                return render_template('orgaLogin.html', error="Invalid credentials")
        
            # MODIFICATION
            action = request.form.get("action")
            if action == "startTournament":
                dbm.WriteTournamentParameters(tournamentDict, "False")
                
                createMatchAttempt=mmm.CreateMatches(tournamentDict["tournamentName"])
                
                if createMatchAttempt==False: return render_template('createTournament.html', parametersList=tournamentList, isCreating=isCreating, isStarted=False, error="Too many teams/matches for the availabilities specified.")
                
                dbm.WriteTournamentParameters(tournamentDict, "True")
                return render_template("orgaLogin.html", validation="Tournament successfully started", parametersList=[])
            if action == "availabilities":
                return redirect(url_for('Availabilities', tournamentName=tournamentDict["tournamentName"], password=tournamentDict["password"]))
            else:
                dbm.WriteTournamentParameters(tournamentDict, "False")
                return render_template("orgaLogin.html", validation="Tournament successfully modified", parametersList=[])


@app.route('/availabilities', methods=['GET', 'POST'])
def Availabilities ():
    tournamentName=request.args.get("tournamentName")
    password=request.args.get("password")
    
    if request.method=="GET":
        availabilitiesList=dbm.GetAvailabilities(tournamentName)

        return render_template("availabilities.html", tournamentName=tournamentName, password=password, availabilitiesList=availabilitiesList)
    elif request.method=="POST":
        if not lm.IsLoginCorrect(tournamentName, password):
            return render_template('orgaLogin.html', error="Invalid credentials")
        if lm.GetParamatersList(tournamentName)[8]=="True":
            return render_template('orgaLogin.html', error="Started tournaments cant be modified")
        
        availabilitiesList=[]
        availabilitiesNumber=request.args.get("availabilitiesNumber")
        for k in range(1, int(availabilitiesNumber)):
            currentAvailability=[]
            print("date"+str(k))
            currentAvailability.append(request.form.get("date"+str(k)))
            currentAvailability.append(request.form.get("duration"+str(k)))
            currentAvailability.append(request.form.get("daysInARow"+str(k)))
            currentAvailability.append(request.form.get("fieldName"+str(k)))
            
            availabilitiesList.append(currentAvailability)
        
        print(availabilitiesList)
        
        a=dbm.UpdateAvailabilities(tournamentName, availabilitiesList)
        
        if a:
            return render_template("availabilities.html", tournamentName=tournamentName, availabilitiesList=[[k+1]+availabilitiesList[k] for k in range(len(availabilitiesList))], error=a)
        
        parametersList = lm.GetParamatersList(tournamentName)
        parametersList.append(password)
        return render_template("createTournament.html", parametersList=parametersList, isCreating=False, isStarted=parametersList[8])


@app.route('/createTeam', methods=['GET', 'POST'])
def CreateTeam():
    tournamentName=request.args.get("tournamentName")
    numberOfPlayers=int(lm.GetParamatersList(tournamentName)[2])
    isCreating=request.args.get("isCreating")=="True"

    if request.method == "GET":

        if isCreating:
            return render_template("createTeam.html", parametersList=[tournamentName], players=[["", ""]]*numberOfPlayers, isCreating=True)
        else:
            teamName=request.args.get("teamName")
            teamPassword=request.args.get("teamPassword")
            
            # Vérifie l'identité de l'équipe
            if not dbm.IsTeamLoginCorrect(tournamentName, teamName, teamPassword):
                return render_template("chiefTeamLogin.html", error="Invalid Password", parametersList=[tournamentName, teamName])
    
            players=[["", ""]]*numberOfPlayers

            rawPlayers=dbm.GetTeamPlayers(tournamentName, teamName)
            for k in range(len(rawPlayers)):
                players[k]=[rawPlayers[k][1], rawPlayers[k][2], rawPlayers[k][3]]

            return render_template("createTeam.html", parametersList=[tournamentName, teamName, teamPassword], players=players, isCreating=False)
    elif request.method=="POST":
        teamPlayers=[]
        for k in range(numberOfPlayers):
            teamPlayers.append([request.form.get(i+str(k)) for i in ["teamMemberFirstName", "teamMemberLastName", "teamMemberShirtNumber"]])
            
        for k in teamPlayers:
            for n in k:
                if n[0]=="" or n[1]=="": render_template("createTeam.html", error="Empty player name", parametersList=[tournamentName, teamName], players=teamPlayers, isCreating=isCreating)

        if isCreating:
            teamName=request.form.get("teamName")
            teamPassword=request.form.get("teamPassword")
            
            if not lm.IsUniqueTeamId(teamName, tournamentName):
                return render_template("createTeam.html", error="Team name already taken", parametersList=[tournamentName, teamName], players=teamPlayers, isCreating=True)
            
            dbm.AddVoidTeam(tournamentName, teamName, teamPassword, numberOfPlayers)
        else:
            print('wtf')
            teamName=request.args.get("teamName")
            teamPassword=request.args.get("teamPassword")
            
            # Vérifie l'identité de l'équipe
            if not dbm.IsTeamLoginCorrect(tournamentName, teamName, teamPassword):
                return render_template("createTeam.html", error="Invalid Password", parametersList=[tournamentName, teamName], players=teamPlayers, isCreating=False)

        dbm.UpdateTeam(tournamentName, teamName, teamPlayers)

        return redirect(url_for("ChiefTeamLogin", validation="team modified successfully"))
        

@app.route('/chiefTeamLogin', methods=['GET', 'POST'])
def ChiefTeamLogin():
    if request.method=="GET":
        return render_template('chiefTeamLogin.html', validation=request.args.get("validation"), parametersList=["", "", ""])
    elif request.method=="POST":
        action=request.form.get("action")
        
        teamDict={}
        teamList=[]
        for k in ["tournamentName", "teamName", "teamPassword", "tournamentNameR"]:
            value=request.form.get(k)
            if value==None: value=""
            teamDict[k]=value
            teamList.append(value)
        
        if action=="create":
            # Vérifie si le tournoi existe
            if not lm.IsExistingTournament(teamDict["tournamentNameR"]):
                return render_template("chiefTeamLogin.html", error="Invalid Tournament Name", parametersList=[])
            
            return redirect(url_for("CreateTeam", tournamentName=teamDict["tournamentNameR"], isCreating=True))
        elif action=="logIn":
            

            # Vérifie que tous les champs sont remplis
            for (key, value) in teamDict.items():
                if value=="": render_template("chiefTeamLogin.html", error=key+" is empty", parametersList=teamList)

            # Vérifie si le tournoi existe
            if not lm.IsExistingTournament(teamDict["tournamentName"]):
                return render_template("chiefTeamLogin.html", error="Invalid Tournament Name", parametersList=teamList)

            # Vérifie l'identité de l'équipe
            if not dbm.IsTeamLoginCorrect(teamDict["tournamentName"], teamDict["teamName"], teamDict["teamPassword"]):
                return render_template("chiefTeamLogin.html", error="Invalid Password", parametersList=[teamDict["tournamentName"], teamDict["teamName"]])

            return redirect(url_for("CreateTeam", tournamentName=teamDict["tournamentName"], teamName=teamDict["teamName"], teamPassword=teamDict["teamPassword"], isCreating=False))
        

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
        
        
        print(parameters, refereePassword)
        if parameters[6] != refereePassword:
            return render_template("refereeLogin.html", error="Invalid referee password", tournamentName=tournamentName)
        
        # Si tout est bon
        currentMatchesList = dbm.GetMatches(tournamentName, False)
        if request.args.get("matchEnded")=="True":
            return render_template("refereeMatchChoice.html", parametersList=[tournamentName, refereePassword], matchesList=currentMatchesList, validation="match fini")
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
        
        if playerId=="startMatch":
            dbm.StartMatch(tournamentName, matchId)
            matchTeams=[dbm.GetTeamPlayers(tournamentName, k) for k in dbm.GetMatch(tournamentName, matchId)[3:5]]
            return render_template("referee.html", parametersList=[tournamentName, refereePassword, matchId], matchInfos=dbm.GetMatch(tournamentName, matchId), teams=matchTeams, validation="match lancé")
        elif playerId=="endMatch":
            dbm.EndMatch(tournamentName, matchId)
            currentMatchesList = dbm.GetMatches(tournamentName, False)
            return redirect(url_for("RefereeMatchChoice", tournamentName=tournamentName, refereePassword=refereePassword, matchEnded=True))
            
        
        pointsScored = request.form.get("pointsScored")
        if pointsScored == "":
            matchTeams=[dbm.GetTeamPlayers(tournamentName, k) for k in dbm.GetMatch(tournamentName, matchId)[3:5]]
            return render_template("referee.html", parametersList=[tournamentName, refereePassword, matchId], matchInfos=dbm.GetMatch(tournamentName, matchId), teams=matchTeams, error="Invalid Point Value")

        result=dbm.AddPoint(tournamentName, matchId, playerId, pointsScored)

        if result!="":
            matchTeams=[dbm.GetTeamPlayers(tournamentName, k) for k in dbm.GetMatch(tournamentName, matchId)[3:5]]
            return render_template("referee.html", parametersList=[tournamentName, refereePassword, matchId], matchInfos=dbm.GetMatch(tournamentName, matchId), teams=matchTeams, error=result)
        
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
        tournamentName = request.form.get("tournamentName")
        if lm.IsExistingTournament(tournamentName):
            return redirect(url_for("Spectator", tournamentName=tournamentName))
        else:
            return render_template("spectatorLogin.html", error="Tournoi Inconnu")


@app.route("/spectator/<tournamentName>", methods=["GET", "POST"])
def Spectator(tournamentName):
    if request.method=="GET":
        return render_template("spectator.html", parametersList=[tournamentName], matchesList=dbm.GetMatches(tournamentName), rankings=dbm.EstablishRankings(tournamentName))
    elif request.method=="POST":
        matchId=request.form.get("matchIdButton")
        return render_template("spectator.html", parametersList=[tournamentName, matchId], points=dbm.GetPoints(tournamentName, matchId), matchInfos=dbm.GetMatchInfos(tournamentName, matchId))
    

@app.route('/favicon.ico', methods=["GET"])
def Favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    configs = cm.GetAppConfig()
    app.run(host=configs["host"], port=int(configs["port"]), debug=configs["debug"]=="True", use_reloader=True)