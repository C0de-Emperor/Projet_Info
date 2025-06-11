import sqlite3, itertools, random, math
from dateutil import parser
from datetime import timedelta
import random
from pythonScripts import loginManager

def GetMatchesNumber (tournamentName:str) -> int:
    return len(GetMatchesAvailabilities(tournamentName))

def GetMatchesAvailabilities (tournamentName:str) -> list:
    matchDuration = int(loginManager.GetParamatersList(tournamentName)[1])
    matches = []

    connexion = sqlite3.connect("databases/"+tournamentName+".db")
    cursor = connexion.cursor()

    availabilities = cursor.execute("""SELECT availabilityId, startTime, duration, daysInARow FROM availabilities""").fetchall()

    for av in availabilities:
        av=list(av)
        a=av[2].split("h")
        if a[1]=="": a[1]=0
        av[2]=int(a[0])*60+int(a[1])
        
        if av[2]//matchDuration >= 1:
            startDate = parser.parse(str(av[1]))
            for i in range(av[2]//matchDuration):
                for k in range(av[3]):
                    matches.append([startDate + timedelta(minutes=matchDuration*i, days=k), av[0]])
            
    connexion.close()
    return matches

def GetTeams (tournamentName:str) -> list:
    connexion = sqlite3.connect("databases/"+tournamentName+".db")
    cursor = connexion.cursor()

    teams = cursor.execute("""SELECT teamName FROM teams""").fetchall()
    connexion.close()

    return [team[0] for team in teams] 

def CreateMatches(tournamentName):
    connexion = sqlite3.connect("databases/" + tournamentName + ".db")
    cursor = connexion.cursor()

    # Données
    availabilities = GetMatchesAvailabilities(tournamentName)
    teams = GetTeams(tournamentName)
    
    combinations = list(itertools.combinations(teams, 2))
    random.shuffle(combinations)
    
    
    print(len(combinations), len(availabilities))
    if len(combinations) > len(availabilities): return False
    
    # Insertion dans la base
    for i, (team1, team2) in enumerate(combinations):
        match_date, avail_id = availabilities[i]
        cursor.execute("INSERT INTO matches (matchDate, matchAvailabilityId, team1Name, team2Name) VALUES (?, ?, ?, ?)", (match_date.strftime("%Y-%m-%d %H:%M:%S"), avail_id, team1, team2))

    connexion.commit()
    connexion.close()

    return True