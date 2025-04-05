import sqlite3

dataBasePath = r"PasswordsDatabase.db"

def IsLoginCorrect(databaseId:str, password:str) -> bool:
    connexion = sqlite3.connect(dataBasePath)
    cursor = connexion.cursor()

    if cursor.execute(f"""SELECT count(*) FROM Login WHERE tournamentId = "{databaseId}" AND password = "{password}";""").fetchone()[0] <= 0:
        return False

    return True

def AddNewLogin(databaseId:str, password:str):
    connexion = sqlite3.connect(dataBasePath)
    cursor = connexion.cursor()

    cursor.execute(f""":INSERT INTO Login (tournamentId, password) VALUES ('{databaseId}', '{password}');""")
    connexion.commit()