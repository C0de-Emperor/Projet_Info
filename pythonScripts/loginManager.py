import sqlite3

dataBasePath = r"passwordsDatabase.db"

def IsLoginCorrect(databaseName:str, password:str) -> bool:
    connexion = sqlite3.connect(dataBasePath)
    cursor = connexion.cursor()

    if cursor.execute(f"""SELECT count(*) FROM Login WHERE tournamentName = "{databaseName}" AND password = "{password}";""").fetchone()[0] <= 0:
        connexion.close()
        return False

    connexion.close()
    return True

def AddNewLogin(databaseId:str, password:str):
    connexion = sqlite3.connect(dataBasePath)
    cursor = connexion.cursor()

    cursor.execute(f"""INSERT INTO Login (tournamentName, password) VALUES ('{databaseId}', '{password}');""")
    connexion.commit()

    connexion.close()

def IsUniqueId (databaseId:str) -> bool:
    connexion = sqlite3.connect(dataBasePath)
    cursor = connexion.cursor()

    if cursor.execute(f"""SELECT count(*) FROM Login WHERE tournamentName = "{databaseId}";""").fetchone()[0] <= 0:
        connexion.close()
        return True

    connexion.close()
    return False

def GetParamatersList(databaseId:str):
    tournamentList=[]
    with open("databases/tournament"+databaseId+"Database.txt", "r") as f:
        lines = f.readlines()
        for k in lines:
            tournamentList.append(k.strip())
    tournamentList.append(databaseId)

    return tournamentList

def IsExistingTournament(databaseId:str) -> bool:
    connexion = sqlite3.connect(dataBasePath)
    cursor = connexion.cursor()

    if cursor.execute(f"""SELECT count(*) FROM Login WHERE tournamentName = "{databaseId}";""").fetchone()[0] <= 0:
        connexion.close()
        return False
    
    connexion.close()
    return True