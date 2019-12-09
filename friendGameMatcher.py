import eel
import setting_secret
import requests
import DB_Handler
import time
import json

from operator import itemgetter
from requests.exceptions import ConnectionError

print("starting friend game matcher")
eel.init("web")
eel.start("main.html", block = False)

def getFriends(id):
    url = 'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?'
    params = {'key': setting_secret.STEAM_KEY, 'steamid': id,"relationship":"friend"}
    r = requests.get(url, params=params)
    friendsListJson = r.json()
    friendIDlist=[]


    if len(friendsListJson) == 0:
        return friendIDlist

    friendslist = friendsListJson["friendslist"]["friends"]

    for friend in friendslist:
        friendIDlist.append(friend["steamid"])

    return friendIDlist


def getFriendsInfo(ids):
    turnlist = []
    if len(ids) > 100:
        chunks = [ids[x:x + 100] for x in range(0, len(ids), 100)]

        for chunk in chunks:
            idsStn = ",".join(chunk)
            url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?'
            params = {'key': setting_secret.STEAM_KEY, 'steamids': idsStn}
            r = requests.get(url, params=params)
            friendsInfoListJson = r.json()
            infoList = friendsInfoListJson["response"]["players"]

            turnlist.extend(sorted(infoList, key=itemgetter('personaname')))

    else:
        idsStn = ",".join(ids)
        url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?'
        params = {'key': setting_secret.STEAM_KEY, 'steamids': idsStn}
        r = requests.get(url, params=params)
        friendsInfoListJson = r.json()
        infoList = friendsInfoListJson["response"]["players"]

        turnlist.extend(sorted(infoList, key=itemgetter('personaname')))

    return turnlist

def getFriendsInfoBySteamID(id):
    return getFriendsInfo(getFriends(id))

def getUserGames(id):
    url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?'
    params = {'key': setting_secret.STEAM_KEY, 'steamid': id}
    r = requests.get(url, params=params)
    gamesList = r.json()
    print(r.url)
    games = gamesList["response"].get("games")
    turnList = []
    if games is None:
        return turnList
    for game in games:
        turnList.append(game["appid"])
    return turnList

def getCommonGames(user,IDs):
    url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?'

    userList = set(getUserGames(user))

    for id in IDs:
        glist = []
        params = {'key': setting_secret.STEAM_KEY, 'steamid': id}
        r = requests.get(url, params=params)
        gamesList = r.json()
        games = gamesList["response"].get("games")

        if games is not None:
            for game in games:
                glist.append(game["appid"])

        userList = userList.intersection(glist)

    return userList

def getGamesInfo(games):
    url = 'https://store.steampowered.com/api/appdetails/basic?'
    gameList = []
    ok = True
    count429 = 0

    for game in games:
        params = {'key': setting_secret.STEAM_KEY,'appids': game}
        try:
            r = requests.get(url, params=params)
        except ConnectionError as e:
            print(e)
            ok = False
            continue
        print(r)
        if r.status_code == 200:
            count429 = 0
            gameInfo = r.json()
            x = gameInfo[str(game)].get("data")

            if x is not None:
                gameList.append(x)
        elif r.status_code == 403:
            ok = False
            return [gameList,ok]
        elif r.status_code == 429:
            count429+=1
            if count429 >10:
                ok = False
                return [gameList, ok]
        else:
            ok = False


    return  [gameList,ok]

def getCommonGamesInfo(user,IDs):
    return getGamesInfo(getCommonGames(user, IDs))

def getSteamByURl(vanityURL):
    url = 'https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?'
    params = {'key': setting_secret.STEAM_KEY, 'vanityurl': vanityURL}
    r = requests.get(url, params=params)
    steamID = r.json()["response"].get("steamid")

    if steamID is not None:
        return steamID
    else:
        return ""

def getUserExists(id):
    url = 'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?'
    params = {'key': setting_secret.STEAM_KEY, 'steamids': id}
    r = requests.get(url, params=params)
    players = r.json()["response"].get("players")

    if len(players) > 0:
        return True
    else:
        return False


@eel.expose
def getMyFriends():
    return getFriendsInfoBySteamID(setting_secret.MyID)


@eel.expose
def getMyCommonGames(ids):
    ids.append(setting_secret.MyID)

    populateDb(ids)

    gamesIDs = DB_Handler.get_common_games(ids)
    game_Info = DB_Handler.get_game_info(gamesIDs)

    return game_Info

@eel.expose
def getRemoteGames(ids):
    ids.append(setting_secret.MyID)
    gamesIDs_remote = DB_Handler.get_remote_games(ids)
    game_Info = DB_Handler.get_game_info(gamesIDs_remote)
    return game_Info

@eel.expose
def getUniqueGames(ids):
    ids.append(setting_secret.MyID)
    gamesIDs_common = DB_Handler.get_common_games(ids)

    tempList = []
    for id in ids:
        tempDict = dict()


        library = DB_Handler.get_library(id)
        for otherID in ids:
            if otherID != id:
                library = library.difference(DB_Handler.get_library(otherID))


        tempDict["steamID"] = id
        tempDict["games"] = DB_Handler.get_game_info(library)

        tempList.append(tempDict)

    print(tempList)
    return tempList



def populateDb(ids):

    for id in ids:
        DB_Handler.add_library_and_game(id,getUserGames(id))

    nullGame = DB_Handler.get_null_games()

    print(len(nullGame))

    populateDb_gameInfo(nullGame)


def populateDb_gameInfo(games):
    url = 'https://store.steampowered.com/api/appdetails/basic?'
    ok = True
    count429 = 0

    for game in games:
        print("getting game info for: ",game)
        params = {'key': setting_secret.STEAM_KEY, 'appids': game}
        try:
            r = requests.get(url, params=params)
        except ConnectionError as e:
            print(e)
            ok = False
            continue
        print(r)
        if r.status_code == 200:
            count429 = 0
            gameInfo = r.json()
            x = gameInfo[str(game)].get("data")

            if x is not None:
                if x["steam_appid"] == game:
                    DB_Handler.add_to_game_info(x)
                else:
                    x["steam_appid"] = game
                    DB_Handler.add_to_game_info(x)
            else:
                DB_Handler.add_null_game(game)
        elif r.status_code == 403:
            ok = False
            return ok
        elif r.status_code == 429:
            count429 += 1
            if count429 > 2:
                ok = False
                return ok
        else:
            ok = False

    return ok





#DB_Handler.delete_DB()
DB_Handler.create_DB()
while True:
    eel.sleep(1)

