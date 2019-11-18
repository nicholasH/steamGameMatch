import eel
import setting_secret
import requests
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
    print(ids)
    print(getCommonGamesInfo(setting_secret.MyID,ids))
    return getCommonGamesInfo(setting_secret.MyID,ids)[0]




while True:
    eel.sleep(1)

