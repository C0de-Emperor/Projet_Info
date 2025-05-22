import sqlite3, loginManager, itertools
from dateutil import parser
from datetime import timedelta
from collections import defaultdict
import random

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

def CreateMatches(tournamentName: str):
    connexion = sqlite3.connect("databases/" + tournamentName + ".db")
    cursor = connexion.cursor()

    # Données
    availabilities = GetMatchesAvailabilities(tournamentName)
    random.shuffle(availabilities)
    teams = GetTeams(tournamentName)
    nTeams = len(teams)

    # Toutes les combinaisons uniques possibles sans doublon
    unique_combinations = list(itertools.combinations(teams, 2))
    random.shuffle(unique_combinations)

    # Ne pas dépasser le nombre de créneaux
    selected_matches = unique_combinations[:len(availabilities)]

    # Suivi des matchs joués par équipe
    match_count = {team: 0 for team in teams}
    for team1, team2 in selected_matches:
        match_count[team1] += 1
        match_count[team2] += 1

    # Insertion dans la base
    for i, (team1, team2) in enumerate(selected_matches):
        match_date, avail_id = availabilities[i]
        cursor.execute("""
            INSERT INTO matches (matchDate, matchAvailabilityId, team1Name, team2Name)
            VALUES (?, ?, ?, ?)""",
            (match_date.strftime("%Y-%m-%d %H:%M:%S"), avail_id, team1, team2)
        )

    connexion.commit()
    connexion.close()
    return None

def GetTeams (tournamentName:str) -> list:
    connexion = sqlite3.connect("databases/"+tournamentName+".db")
    cursor = connexion.cursor()

    teams = cursor.execute("""Select teamName From teams""").fetchall()
    connexion.close()

    return [team[0] for team in teams] 

