import sqlite3

createDatabaseInstructions = [
        "CREATE TABLE teams (teamName VARCHAR(50));",
        "CREATE TABLE players (playerId INTEGER PRIMARY KEY, playerName VARCHAR(50), playerFirstName VARCHAR(20), playerTeam VARCHAR(50) REFERENCES teams(teamName), isTeamChief BOOLEAN);",
        "CREATE TABLE fields (fieldName VARCHAR(50) PRIMARY KEY);",
        "CREATE TABLE matches (matchId INTEGER PRIMARY KEY AUTOINCREMENT, matchDate DATETIME, matchFieldId INTEGER REFERENCES fields(fieldId), team1Name VARCHAR(50) REFERENCES teams(teamName), team2Name VARCHAR(50) REFERENCES teams(teamName))",
        "CREATE TABLE points (pointId INTEGER PRIMARY KEY AUTOINCREMENT, matchId INTEGER REFERENCES matches(matchId), playerId INTEGER REFERENCES players(playerId), numberOfPoints INTEGER, team1Scored BOOLEAN);"
    ]

def createTournament(tournamentId, tournamentDict):
    
    f=open("tournament"+tournamentId+"Database.db", "w")
    f.close()

    connexion = sqlite3.connect("tournament"+tournamentId+"Database.db")
    cursor = connexion.cursor()

    for k in createDatabaseInstructions:
        cursor.execute(k)
    connexion.commit()

    connexion.close()

    with open(databasePath+databaseName+".csv", "w") as f:
        for (keys, values) in tournamentDict.items():
            f.write(values+"\n")
    
    return ""


def addTeam(teamName, teamPlayers, teamChiefIndex, tournamentId):

    for k in range(len(teamPlayers)):
        if len(teamPlayers[k])!=2: return "player n°"+str(k+1)+" has a problem of arguments"

    connexion = sqlite3.connect("tournament"+tournamentId+"Database.db")
    cursor = connexion.cursor()

    cursor.execute("SELECT playerId FROM players ORDER BY playerId DESC;")
    lastPlayerId = cursor.fetchone()
    if lastPlayerId == None:
        lastPlayerId=-1

    cursor.execute("INSERT INTO teams VALUES (?)", (teamName,))

    for k in range(len(teamPlayers)):
        cursor.execute("INSERT INTO players VALUES (?, ?, ?, ?, ?)", (lastPlayerId+k+1, teamPlayers[k][0], teamPlayers[k][1], teamName, (k==teamChiefIndex)))
    connexion.commit()

    connexion.close()

    return ""


def addFields(fieldsList, tournamentId):

    connexion = sqlite3.connect("tournament"+tournamentId+"Database.db")
    cursor = connexion.cursor()

    for k in fieldsList:
        cursor.execute("INSERT INTO fields VALUES (?)", (k,))
    connexion.commit()

    connexion.close()

    return ""


def addMatches(matchesList, tournamentId):

    for k in range(len(matchesList)):
        if len(matchesList[k])!=4: return "match n°"+str(k+1)+" has a problem of arguments"
        if type(matchesList[k][0])!=str: return "the date of match n°"+str(k+1)+" should be a string"
        if type(matchesList[k][1])!=int: return "the fieldNumber of n°"+str(k+1)+" should be an integer"

    connexion = sqlite3.connect("tournament"+tournamentId+"Database.db")
    cursor = connexion.cursor()

    cursor.execute("SELECT matchId FROM matches ORDER BY matchID DESC;")
    lastMatchId = cursor.fetchone()
    if lastMatchId == None:
        lastMatchId=-1

    for k in range(len(matchesList)):
        currentMatch = matchesList[k]
        cursor.execute("INSERT INTO matches VALUES (?, ?, ?, ?, ?);", (lastMatchId+1+k, currentMatch[0], currentMatch[1], currentMatch[2], currentMatch[3]))
    connexion.commit()

    connexion.close()

    return ""


def addPoint(matchId, playerId, numberOfPoints, team1Scored, tournamentId):

    if type(matchId)!=int: return "matchId should be an integer"
    if type(playerId)!=int: return "playerId should be an integer"
    if type(numberOfPoints)!=int: return "numberOfPoints should be an integer"
    if type(team1Scored)!=bool: return "team1Scored should be a boolean"

    connexion = sqlite3.connect("tournament"+tournamentId+"Database.db")
    cursor = connexion.cursor()

    cursor.execute("SELECT pointId FROM points ORDER BY points DESC;")
    lastPointId = cursor.fetchone()
    if lastPointId == None:
        lastPointId=-1

    cursor.execute("INSERT INTO points VALUES (?, ?, ?, ?, ?)", (lastPointId+1, matchId, playerId, numberOfPoints, team1Scored))
    lastPointId+=1

    connexion.close()

    return ""


