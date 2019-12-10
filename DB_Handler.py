import os
import sqlite3
import sys
import pickle


DBVersion = "0.1"

# library table
library_table = "labrary_table"

steam_ID_field = "steam_id"
game_id_field = "game_id_field"

# game info table
game_info_table = "game_info_table"

# key game_id_field
game_name_field = "game_name"
game_image_field = "game_image_url"
game_categories_field = "game_categories"
is_remote_play_field = "is_remote_play"
is_previously_queried_field = "is_previously_queried"

# data types
integer_field_type = 'INTEGER'
string_field_type = 'STRING'

# The database
dbName = "steam_match.db"
db_path = os.path.join(sys.path[0], dbName)



# creates all the DBs tables
def create_DB():
    create_library_table()
    create_game_info_table()


def get_DB_path():
    global db_path
    return db_path


def create_library_table():
    conn = sqlite3.connect(get_DB_path())
    c = conn.cursor()
    exe = "CREATE TABLE IF NOT EXISTS {tn} (" \
          " {steamID} {fti}," \
          " {gameID} {fti}," \
          "  UNIQUE({steamID},{gameID})) ".format(
        tn=library_table,
        steamID=steam_ID_field,
        gameID=game_id_field,
        fti=integer_field_type
    )

    c.execute(exe)
    conn.commit()
    conn.close()


def create_game_info_table():
    conn = sqlite3.connect(get_DB_path())
    c = conn.cursor()
    exe = "CREATE TABLE IF NOT EXISTS {tn} (" \
          " {gameID} {fti} PRIMARY KEY," \
          " {gameName} {fts}," \
          " {gameImg} {fts}," \
          " {cat} {fts}," \
          " {irp} {fti}, " \
          " {ipq} {fti} )".format(
        tn=game_info_table,
        gameID=game_id_field,
        gameName=game_name_field,
        gameImg=game_image_field,
        cat=game_categories_field,
        irp=is_remote_play_field,
        ipq=is_previously_queried_field,
        fti=integer_field_type,
        fts=string_field_type,
    )

    c.execute(exe)
    conn.commit()
    conn.close()


# deletes the DB
def delete_DB():
    conn = sqlite3.connect(get_DB_path())
    c = conn.cursor()

    c.execute('DROP TABLE IF EXISTS ' + library_table)
    c.execute('DROP TABLE IF EXISTS ' + game_info_table)

    conn.commit()
    conn.close()


# adds info to the DB
def add_to_library(steamID,games):
    manyList = []

    for game in games:
        manyList.append([steamID, game])

    conn = sqlite3.connect(get_DB_path())
    c = conn.cursor()

    exe = "INSERT OR IGNORE INTO {tn} VALUES " \
          " (?,?)".format(
        tn=library_table,
    )

    c.executemany(exe, manyList)
    conn.commit()
    conn.close()


def add_to_game_info(gameInfo):
    conn = sqlite3.connect(get_DB_path())
    c = conn.cursor()



    gameID = gameInfo["steam_appid"]
    gameName = gameInfo["name"]
    gameImage = gameInfo["header_image"]

    print(gameID)
    isRemotePlay = False

    try:
        gameCategories = gameInfo["categories"]

        for cat in gameCategories:
            if cat["id"] == 44:
                isRemotePlay = True

    except KeyError as  e:
        print(e)
        gameCategories = None



    pickledGameCategories = pickle.dumps(gameCategories)

    has_been_queried = True

    exe = "INSERT OR REPLACE INTO {tn} VALUES " \
          " (?,?,?,?,?,?)".format(
        tn=game_info_table,
    )

    c.execute(exe,(gameID,gameName,gameImage,pickledGameCategories,isRemotePlay,has_been_queried))
    conn.commit()
    conn.close()

def add_ids_to_game_info(ids):
    conn = sqlite3.connect(get_DB_path())
    c = conn.cursor()

    manyList = []

    for gameID in ids:
        manyList.append([gameID, None, None, None,None,0])

    exe = "INSERT OR IGNORE INTO {tn} VALUES " \
          " (?,?,?,?,?,?)".format(
        tn=game_info_table,
    )

    c.executemany(exe,manyList)
    conn.commit()
    conn.close()

def add_library_and_game(id,gameIds):
    add_to_library(id,gameIds)
    add_ids_to_game_info(gameIds)

def add_null_game(gameID):
    conn = sqlite3.connect(get_DB_path())
    c = conn.cursor()
    has_been_queried = True

    exe = "INSERT OR REPLACE  INTO {tn} VALUES " \
          " (?,?,?,?,?,?)".format(
        tn=game_info_table,
    )

    c.execute(exe, (gameID, None , None, None, None, has_been_queried))
    conn.commit()
    conn.close()

#getters

def get_library(steamID):
    conn = sqlite3.connect(get_DB_path())
    c = conn.cursor()

    exe = "SELECT {gameID} FROM {tn} " \
              "WHERE {steamID} = {id}".format(
            tn=library_table,
            gameID=game_id_field,
            steamID=steam_ID_field,
            id=steamID
        )

    c.execute(exe)

    conn.commit()
    data = c.fetchall()
    conn.close()

    setTurn = set()
    for d in data:
        setTurn.add(d[0])
    return setTurn

def get_null_games():
    conn = sqlite3.connect(get_DB_path())
    c = conn.cursor()

    exe = "SELECT {gameID} FROM {tn} " \
          " WHERE {gameName} is NULL" \
          " And {ipq} = 0".format(
        tn=game_info_table,
        gameID=game_id_field,
        gameName=game_name_field,
        ipq=is_previously_queried_field
    )

    c.execute(exe)

    conn.commit()
    data = c.fetchall()
    conn.close()

    listTurn = []
    for d in data:
        listTurn.append(d[0])
    return listTurn

def get_common_games(ids):
    conn = sqlite3.connect(get_DB_path())
    c = conn.cursor()

    common_games = set()

    for id in ids:
        exeSub = "SELECT {gameID} FROM {tn} " \
              "WHERE {steamID} = {id}".format(
            tn=library_table,
            gameID=game_id_field,
            steamID=steam_ID_field,
            id=id
        )

        c.execute(exeSub)

        conn.commit()
        data = c.fetchall()

        tempSet = set()
        for d in data:
            tempSet.add(d[0])

        if len(common_games) == 0:
            common_games.update(tempSet)
        else:
            common_games = common_games.intersection(tempSet)

    conn.close()

    return common_games

def get_remote_games(ids):
    conn = sqlite3.connect(get_DB_path())
    c = conn.cursor()

    remote_play_games_set = set()

    for id in ids:
        exeSub = "SELECT {tn1}.{gameID} FROM {tn1}" \
                 " INNER JOIN {tn2} ON {tn1}.{gameID} = {tn2}.{gameID}" \
                 " WHERE {steamID} = {id} AND {irp} = 1".format(
            tn1=library_table,
            tn2=game_info_table,
            gameID=game_id_field,
            steamID=steam_ID_field,
            irp = is_remote_play_field,
            id=id
        )

        c.execute(exeSub)

        conn.commit()
        data = c.fetchall()

        for d in data:
            remote_play_games_set.add(d[0])

    conn.close()

    return remote_play_games_set

def get_game_info(gameIDs):
    conn = sqlite3.connect(get_DB_path())
    c = conn.cursor()

    games_info_list = []

    for id in gameIDs:
        exeSub = "SELECT * FROM {tn} " \
                 "WHERE {gameID} = {id}".format(
            tn=game_info_table,
            gameID=game_id_field,
            id=id
        )

        c.execute(exeSub)

        conn.commit()
        data = c.fetchall()

        games_info_list.append(data[0])

    conn.close()

    return make_dict(games_info_list)



def print_library_table():
    conn = sqlite3.connect(get_DB_path())
    c = conn.cursor()
    exe = "SELECT * FROM " + library_table
    c.execute(exe)
    conn.commit()
    rows = c.fetchall()
    for row in rows:
        print(row)

    conn.close()


def print_game_info_table():
    conn = sqlite3.connect(get_DB_path())
    c = conn.cursor()
    exe = "SELECT * FROM " + game_info_table
    c.execute(exe)
    conn.commit()
    rows = c.fetchall()
    for row in rows:
        print(row)

    conn.close()

def make_dict(list):

    returnList = []
    for x in list:
        returnDic = dict()
        if x[1] is not None:
            returnDic["app_id"] = x[0]
            returnDic["name"] = x[1]
            returnDic["image"] = x[2]
            cat =  pickle.loads(x[3]);
            returnDic["categories"] = [] if (cat is None) else cat

            returnList.append(returnDic)

    return returnList