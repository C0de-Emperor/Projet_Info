import sqlite3

createDatabaseInstructions = [
        "CREATE TABLE teams (teamName VARCHAR(50) PRIMARY KEY, teamPassword VARCHAR(20));",
        "CREATE TABLE players (playerId AUTOINCREMENT INTEGER PRIMARY KEY, playerName VARCHAR(50), playerFirstName VARCHAR(20), playerTeam VARCHAR(50) REFERENCES teams(teamName), isTeamChief BOOLEAN);",
        "CREATE TABLE fields (fieldName VARCHAR(50) PRIMARY KEY);",
        "CREATE TABLE matches (matchId INTEGER PRIMARY KEY AUTOINCREMENT, matchDate DATETIME, matchFieldName VARCHAR(50) REFERENCES fields(fieldId), team1Name VARCHAR(50) REFERENCES teams(teamName), team2Name VARCHAR(50) REFERENCES teams(teamName))",
        "CREATE TABLE points (pointId INTEGER PRIMARY KEY AUTOINCREMENT, matchId INTEGER REFERENCES matches(matchId), playerId INTEGER REFERENCES players(playerId), numberOfPoints INTEGER, team1Scored BOOLEAN);"
    ]

def WriteTournamentParameters(tournamentName, tournamentDict):
    with open("databases/tournament"+tournamentName+"Database.txt", "w") as f:
        for (keys, values) in tournamentDict.items():
            f.write(values+"\n")

def CreateTournament(tournamentName, tournamentDict):
    
    f=open("databases/tournament"+tournamentName+"Database.db", "w")
    f.close()

    connexion = sqlite3.connect("databases/tournament"+tournamentName+"Database.db")
    cursor = connexion.cursor()

    for k in createDatabaseInstructions:
        cursor.execute(k)
    connexion.commit()

    connexion.close()

    WriteTournamentParameters(tournamentName, tournamentDict)
    
    return ""

def AddTeam(teamName, teamPlayers, teamChiefIndex, tournamentName):

    for k in range(len(teamPlayers)):
        if len(teamPlayers[k])!=2: return "player n°"+str(k+1)+" has a problem of arguments"

    connexion = sqlite3.connect("databases/tournament"+tournamentName+"Database.db")
    cursor = connexion.cursor()

    cursor.execute("INSERT INTO teams VALUES (?)", (teamName,))

    for k in range(len(teamPlayers)):
        cursor.execute("INSERT INTO players(playerName, playerFirstName, playerTeam, isTeamChief) VALUES (?, ?, ?, ?)", (teamPlayers[k][0], teamPlayers[k][1], teamName, (k==teamChiefIndex)))
    connexion.commit()

    connexion.close()

    return ""

def AddFields(fieldsList, tournamentName):

    connexion = sqlite3.connect("databases/tournament"+tournamentName+"Database.db")
    cursor = connexion.cursor()

    for k in fieldsList:
        cursor.execute("INSERT INTO fields VALUES (?)", (k,))
    connexion.commit()

    connexion.close()

    return ""

def AddMatches(matchesList, tournamentName):

    for k in range(len(matchesList)):
        if len(matchesList[k])!=4: return "match n°"+str(k+1)+" has a problem of arguments"
        if type(matchesList[k][0])!=str: return "the date of match n°"+str(k+1)+" should be a string"
        if type(matchesList[k][1])!=int: return "the fieldNumber of n°"+str(k+1)+" should be an integer"

    connexion = sqlite3.connect("databases/tournament"+tournamentName+"Database.db")
    cursor = connexion.cursor()

    for k in range(len(matchesList)):
        currentMatch = matchesList[k]
        cursor.execute("INSERT INTO matches(matchDate, matchFieldName, team1Name, team2Name) VALUES (?, ?, ?, ?);", (currentMatch[0], currentMatch[1], currentMatch[2], currentMatch[3]))
    connexion.commit()

    connexion.close()

    return ""

def AddPoint(matchId, playerId, numberOfPoints, team1Scored, tournamentName):

    if type(matchId)!=int: return "matchId should be an integer"
    if type(playerId)!=int: return "playerId should be an integer"
    if type(numberOfPoints)!=int: return "numberOfPoints should be an integer"
    if type(team1Scored)!=bool: return "team1Scored should be a boolean"

    connexion = sqlite3.connect("databases/tournament"+tournamentName+"Database.db")
    cursor = connexion.cursor()

    cursor.execute("INSERT INTO points(matchId, playerId, numberOfPoints, team1Scored) VALUES (?, ?, ?, ?)", (matchId, playerId, numberOfPoints, team1Scored))
    lastPointId+=1

    connexion.close()

    return ""

def IsTeamLoginCorrect (databasePath:str, teamName:str, teamPassword) -> bool:
    connexion = sqlite3.connect(databasePath)
    cursor = connexion.cursor()

    if cursor.execute(f"""SELECT count(*) FROM teams WHERE teamName = "{teamName}" AND password = "{teamPassword}";""").fetchone()[0] <= 0:
        connexion.close()
        return False

    connexion.close()
    return True











def GetMatches(tournamentName):
    connexion = sqlite3.connect("databases/tournament"+tournamentName+"Database.db")
    cursor = connexion.cursor()
    print(tournamentName)

    cursor.execute("SELECT * from matches;")
    matchesList = cursor.fetchall()

    connexion.close()

    return matchesList

def GetMatch(tournamentName, matchId):
    matchesList=GetMatches(tournamentName)
    print(matchId)

    for k in matchesList:
        if k[0]==int(matchId):
            return k
    
    return None


def GetTeamPlayers(tournamentName, teamName):
    connexion = sqlite3.connect("databases/tournament"+tournamentName+"Database.db")
    cursor = connexion.cursor()

    cursor.execute("SELECT * from players WHERE playerTeam = ?", (teamName, ))
    playersList = cursor.fetchall()

    connexion.close()

    return playersList