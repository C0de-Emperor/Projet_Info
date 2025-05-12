import sqlite3, loginManager, itertools
from dateutil import parser
from datetime import timedelta

def GetMatchesNumber (tournamentName:str) -> int:
    return len(GetMatchesAvailabilities(tournamentName))

def GetMatchesAvailabilities (tournamentName:str) -> list:
    matchDuration = int(loginManager.GetParamatersList(tournamentName)[1])
    matches = []

    connexion = sqlite3.connect("databases/"+tournamentName+".db")
    cursor = connexion.cursor()

    availabilities = cursor.execute("""Select availabilityId, startTime, duration, daysInARow From availabilities""").fetchall()

    for av in availabilities:
        if av[2]//matchDuration >= 1:
            startDate = parser.parse(str(av[1]))
            for i in range(av[2]//matchDuration):
                for k in range(av[3]):
                    matches.append([startDate + timedelta(minutes=matchDuration*i, days=k), av[0]])
            
    connexion.close()
    return matches

def CreateMatches (tournamentName:str):
    connexion = sqlite3.connect("databases/"+tournamentName+".db")
    cursor = connexion.cursor()

    combinations = [l for l in itertools.combinations(GetTeams(tournamentName),2)]
    NComb = len(combinations)
    NAvailabilities = GetMatchesNumber(tournamentName)
    availabilities = GetMatchesAvailabilities (tournamentName)

    if NAvailabilities < NComb:
        return "pas assez de crenaux disponibles" # retourner une erreur
    
    if NComb < 3:
        return "Pas assez de matchs" # retourner une erreur
    
    i = 0
    for comb in combinations:
        cursor.execute(f"""INSERT INTO matches (matchDate, matchAvailabilityId, team1Name, team2Name) VALUES ("{availabilities[i][0].strftime("%Y-%m-%d %H:%M:%S")}", {availabilities[i][1]}, "{comb[0]}", "{comb[1]}")""")
        i += 1

    connexion.commit()
    connexion.close()

    return None
    
def GetTeams (tournamentName:str) -> list:
    connexion = sqlite3.connect("databases/"+tournamentName+".db")
    cursor = connexion.cursor()

    teams = cursor.execute("""Select teamName From teams""").fetchall()
    connexion.close()

    return [team[0] for team in teams] 
