import sqlite3, datetime

separator = "%Separator%"

createDatabaseInstructions = [
        "CREATE TABLE teams (teamName VARCHAR(50) PRIMARY KEY, teamPassword VARCHAR(20));",
        "CREATE TABLE players (playerId  INTEGER PRIMARY KEY AUTOINCREMENT, playerName VARCHAR(50), playerFirstName VARCHAR(20), playerShirtNumber INTEGER, playerTeam VARCHAR(50) REFERENCES teams(teamName), isTeamChief BOOLEAN DEFAULTS false);",
        "CREATE TABLE availabilities (availabilityId INTEGER AUTOINCREMENT PRIMARY KEY, startTime DATETIME, duration INTEGER, daysInARow INTEGER, fieldName VARCHAR(50));",
        "CREATE TABLE matches (matchId INTEGER PRIMARY KEY AUTOINCREMENT, matchDate DATETIME, matchAvailabilityId VARCHAR(50) REFERENCES availabilities(availabilityId), team1Name VARCHAR(50) REFERENCES teams(teamName), team2Name VARCHAR(50) REFERENCES teams(teamName), startTime DATETIME)",
        "CREATE TABLE points (pointId INTEGER PRIMARY KEY AUTOINCREMENT, matchId INTEGER REFERENCES matches(matchId), playerId INTEGER REFERENCES players(playerId), numberOfPoints INTEGER, dateOfPointSubmit DATETIME);"
    ]

def WriteTournamentParameters(tournamentDict:dict, isTournamentStarted:bool):#tournamentName:str, _sport:str, _duration:str, _teamSize:str, _terrain:str, _algo:str, _maxTeam:str, _selection:str, _points:str, _refP:str, tournamentAccessibilityState:bool): 
    with open("databases/"+tournamentDict["tournamentName"]+".txt", "w") as f:
        for param in ["sport", "matchDuration", "teamSize", "availableSportFields", "algorithm", "maxTeamNumber", "teamSelectionMethod", "points", "refereePassword", "tournamentName"]:
            print([tournamentDict[param]])
            f.write(tournamentDict[param] + separator)
        f.write(isTournamentStarted+separator)

def CreateTournament(tournamentName, tournamentDict, access:str):
    
    f=open("databases/"+tournamentName+".db", "w")
    f.close()

    connexion = sqlite3.connect("databases/"+tournamentName+".db")
    cursor = connexion.cursor()

    for k in createDatabaseInstructions:
        cursor.execute(k)
    connexion.commit()

    connexion.close()
    WriteTournamentParameters(tournamentDict, str(access))

def AddTeam(tournamentName, teamName, teamPlayers, teamChiefIndex, password):

    for k in range(len(teamPlayers)):
        if len(teamPlayers[k])!=2: return "player n°"+str(k+1)+" has a problem of arguments"

    connexion = sqlite3.connect("databases/"+tournamentName+".db")
    cursor = connexion.cursor()

    cursor.execute("INSERT INTO teams VALUES (?, ?)", (teamName, password))

    for k in range(len(teamPlayers)):
        cursor.execute("INSERT INTO players(playerName, playerFirstName, playerTeam, isTeamChief) VALUES (?, ?, ?, ?)", (teamPlayers[k][0], teamPlayers[k][1], teamName, (k==teamChiefIndex)))
    connexion.commit()

    connexion.close()

    return ""

def AddFields(tournamentName, fieldsList):

    connexion = sqlite3.connect("databases/"+tournamentName+".db")
    cursor = connexion.cursor()

    for k in fieldsList:
        cursor.execute("INSERT INTO fields VALUES (?)", (k,))
    connexion.commit()

    connexion.close()

    return ""

def AddMatches(tournamentName, matchesList):

    for k in range(len(matchesList)):
        if len(matchesList[k])!=4: return "match n°"+str(k+1)+" has a problem of arguments"
        if type(matchesList[k][0])!=str: return "the date of match n°"+str(k+1)+" should be a string"
        if type(matchesList[k][1])!=int: return "the fieldNumber of n°"+str(k+1)+" should be an integer"

    connexion = sqlite3.connect("databases/"+tournamentName+".db")
    cursor = connexion.cursor()

    for k in range(len(matchesList)):
        currentMatch = matchesList[k]
        cursor.execute("INSERT INTO matches(matchDate, matchFieldName, team1Name, team2Name) VALUES (?, ?, ?, ?);", (currentMatch[0], currentMatch[1], currentMatch[2], currentMatch[3]))
    connexion.commit()

    connexion.close()

    return ""

def AddPoint(tournamentName, matchId, playerId, numberOfPoints):

    try:
        matchId=int(matchId)
    except:
        return "matchId should be an integer"
    try:
        playerId=int(playerId)
    except:
        return "playerId should be an integer"
    try:
        numberOfPoints=int(numberOfPoints)
    except:
        return "numberOfPoints should be an integer"

    connexion = sqlite3.connect("databases/"+tournamentName+".db")
    cursor = connexion.cursor()

    cursor.execute("INSERT INTO points(matchId, playerId, numberOfPoints, dateOfPointSubmit) VALUES (?, ?, ?, ?)", (matchId, playerId, numberOfPoints, str(datetime.datetime.now())))
    connexion.commit()

    connexion.close()

    return ""

def IsTeamLoginCorrect (tournamentName:str, teamName:str, teamPassword:str) -> bool:
    connexion = sqlite3.connect("databases/"+tournamentName+".db")
    cursor = connexion.cursor()

    if cursor.execute(f"""SELECT count(*) FROM teams WHERE teamName = "{teamName}" AND teamPassword = "{teamPassword}";""").fetchone()[0] <= 0:
        connexion.close()
        return False

    connexion.close()
    return True

def UpdateTeam (tournamentName:str, teamName:str, teamPlayers:str):
    connexion = sqlite3.connect("databases/"+tournamentName+".db")
    cursor = connexion.cursor()

    cursor.execute("SELECT MIN(playerId) FROM players WHERE playerTeam=?", (teamName, ))
    minPlayerId=cursor.fetchone()[0]

    for k in range(len(teamPlayers)):
        cursor.execute("UPDATE players SET playerName=?, playerFirstName=?, playerShirtNumber=? WHERE playerTeam=? AND playerId=?", (teamPlayers[k][0], teamPlayers[k][1], teamPlayers[k][2], teamName, minPlayerId+k))
    connexion.commit()

    connexion.close()

def GetMatches(tournamentName):
    connexion = sqlite3.connect("databases/"+tournamentName+".db")
    cursor = connexion.cursor()

    cursor.execute("SELECT * from matches;")
    matchesList = cursor.fetchall()

    connexion.close()

    return matchesList

def GetMatch(tournamentName, matchId):
    matchesList=GetMatches(tournamentName)

    for k in matchesList:
        if k[0]==int(matchId):
            return k
    
    return None

def GetTeamPlayers(tournamentName, teamName):
    connexion = sqlite3.connect("databases/"+tournamentName+".db")
    cursor = connexion.cursor()

    cursor.execute("SELECT * from players WHERE playerTeam = ?", (teamName, ))
    playersList = cursor.fetchall()

    connexion.close()

    return playersList

def GetPoints(tournamentName, matchId):
    connexion = sqlite3.connect("databases/"+tournamentName+".db")
    cursor = connexion.cursor()

    cursor.execute("SELECT * FROM points WHERE matchId = ?", (matchId, ))
    pointsList = cursor.fetchall()

    newPointsList=[]
    for k in pointsList:
        cursor.execute("SELECT playerFirstName, playerName, playerTeam FROM players WHERE playerId=?;", (k[2],))
        playerInfos=cursor.fetchone()

        cursor.execute("SELECT team1Name, team2Name FROM matches WHERE matchId = ?", (matchId, ))
        teamsNames=cursor.fetchall()

        newPointsList.append(list(playerInfos)+[k[3], k[4][11:19]])

    connexion.close()

    return newPointsList

def AddVoidTeam(tournamentName, teamName, teamPassword, numberOfPlayers):
    connexion = sqlite3.connect("databases/"+tournamentName+".db")
    cursor = connexion.cursor()

    cursor.execute("INSERT INTO teams VALUES (?, ?)", (teamName, teamPassword))

    cursor.execute("INSERT INTO players(playerTeam, isTeamChief) VALUES (?, true)", (teamName, ))
    for k in range(numberOfPlayers-1):
        cursor.execute("INSERT INTO players(playerTeam) VALUES (?)", (teamName, ))

    connexion.commit()

    connexion.close()

def GetAvailabilities(tournamentName):
    connexion = sqlite3.connect("databases/"+tournamentName+".db")
    cursor = connexion.cursor()

    cursor.execute("SELECT * FROM availabilities")
    availabilitiesList=cursor.fetchall()

    connexion.close()

    return availabilitiesList

def UpdateAvailabilities(tournamentName, availabilitiesList):
    connexion = sqlite3.connect("databases/"+tournamentName+".db")
    cursor = connexion.cursor()
    
    cursor.execute("SELECT availabilityId FROM availabilities ORDER BY availabilityId DESC")
    maxId=cursor.fetchone()[0]
    
    print(maxId, availabilitiesList)
    
    for k in range(maxId+1):
        print(tuple(availabilitiesList[k])+(k, ))
        cursor.execute("UPDATE availabilities SET startTime=?, duration=?, daysInARow=?, fieldName=? WHERE availabilityId=?;", tuple(availabilitiesList[k])+(k, ))
    
    for k in range(maxId+1, len(availabilitiesList)):
        print(tuple(availabilitiesList[k])+(k, ))
        cursor.execute("INSERT INTO availabilities (availabilityId, startTime, duration, daysInARow, fieldName) VALUES (?, ?, ?, ?, ?);", (k,)+tuple(availabilitiesList[k]))
    
    connexion.commit()
    connexion.close()