# https://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972

from flask import Flask, render_template, request, redirect, url_for
from flaskext.mysql import MySQL
from pprint import pprint
from scipy.stats import linregress

import os
import json
import requests
import time
import objectpath

app = Flask(__name__, template_folder="templates")
mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'lol'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

API_KEY = "RGAPI-374b8197-92df-4f67-b81a-950e7adabc24"
BASE_URL = "https://na1.api.riotgames.com/lol/"

VALID_GAME_MODES = ["CLASSIC", "ARAM"]

@app.route("/", methods=['GET','POST'])
def index():
    _getServerChallengerMatches()
    if request.method == 'POST':
        name = request.form.get('playerName')
        return redirect(url_for('player', summonerName=name))
    return render_template("index.html")


def _getServerChampionRatios():
    dumpFile = "championratios.json"
    if os.path.exists(dumpFile):
        with open(dumpFile, 'r') as f:
            return json.load(f)

    playersUrl = "%sleague/v3/masterleagues/by-queue/RANKED_SOLO_5x5?api_key=%s" % (BASE_URL, API_KEY)
    playersJsonResponse = _request(playersUrl)
    summonerIDList = [player["playerOrTeamId"] for player in playersJsonResponse["entries"]]

    playersChampionRatios = {}
    playersNum = 1

    for summonerID in summonerIDList:
        print playersNum

        accountUrl = "%ssummoner/v3/summoners/%s?api_key=%s" % (BASE_URL, summonerID, API_KEY)
        accountJsonResponse = _request(accountUrl)
        if "accountId" not in accountJsonResponse.keys():
            continue
        accountID = accountJsonResponse["accountId"]

        matchlistUrl = "%smatch/v3/matchlists/by-account/%s?api_key=%s" % (BASE_URL, accountID, API_KEY)
        matchlistJsonResponse = _request(matchlistUrl)
        if "matches" not in matchlistJsonResponse.keys():
            continue
        matchlistData = matchlistJsonResponse["matches"]
        
        matchlistSize = len(matchlistData)
        playersChampionRatios.setdefault(accountID, {})

        for match in matchlistData:
            championID = match["champion"]
            if playersChampionRatios[accountID].has_key(championID):
                playersChampionRatios[accountID][championID] += 1.0 / matchlistSize
            else:
                playersChampionRatios[accountID][championID] = 1.0 / matchlistSize

        playersNum += 1
        time.sleep(1.3)

    with open(dumpFile, 'w') as f:
        json.dump(playersChampionRatios, f)
    return 

def _getServerChallengerMatches():
    dumpFile = "challengerMatches.json"
    if os.path.exists(dumpFile):
        with open(dumpFile, 'r') as f:
            return json.load(f)

    playersUrl = "%sleague/v3/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key=%s" % (BASE_URL, API_KEY)
    playersJsonResponse = _request(playersUrl)
    summonerIDList = [player["playerOrTeamId"] for player in playersJsonResponse["entries"]]

    challengerMatches = {}
    playersNum = 1

    for summonerID in summonerIDList:
        print playersNum

        accountUrl = "%ssummoner/v3/summoners/%s?api_key=%s" % (BASE_URL, summonerID, API_KEY)
        accountJsonResponse = _request(accountUrl)
        if "accountId" not in accountJsonResponse.keys():
            continue
        accountID = accountJsonResponse["accountId"]

        matchlistUrl = "%smatch/v3/matchlists/by-account/%s?api_key=%s" % (BASE_URL, accountID, API_KEY)
        matchlistJsonResponse = _request(matchlistUrl)
        if "matches" not in matchlistJsonResponse.keys():
            continue
        matchlistData = matchlistJsonResponse["matches"]

        for match in matchlistData:
            gameId = match["gameId"]
            if match["gameId"] in challengerMatches: 
                continue
            matchUrl = "%smatch/v3/matches/%s?api_key=%s" % (BASE_URL, match["gameId"], API_KEY)
            matchJsonResponse = _request(matchUrl)
            if "gameId" not in matchJsonResponse.keys():
                continue

            challengerMatches[gameId] =  {
                "winner": matchJsonResponse["teams"][0]["win"] == "Fail",
                "players": [],
                "champions": [],
                "items": []
            }

            for player in matchJsonResponse["participantIdentities"]:
                challengerMatches[gameId]["players"].append(player["player"]["accountId"])

            for player in matchJsonResponse["participants"]:
                challengerMatches[gameId]["champions"].append(player["championId"])
                challengerMatches[gameId]["items"].append([
                    player["stats"]["item0"],
                    player["stats"]["item1"],
                    player["stats"]["item2"],
                    player["stats"]["item3"],
                    player["stats"]["item4"],
                    player["stats"]["item5"],
                    ]) 

            time.sleep(1.3)
            print challengerMatches[gameId]

        playersNum += 1
        time.sleep(1.3)

    with open(dumpFile, 'w') as f:
        json.dump(challengerMatches, f)
    return


#https://github.com/jteo1/LoL-Champion-Recommender/blob/master/ChampionRecommendation.py
@app.route("/recommendChamps/<summonerName>",  methods=['GET'])
def recommendChamps(summonerName):
    player(summonerName);
    cursor.execute("select playerID from player where summonerName = '%s'" % (summonerName))
    playerID = cursor.fetchone()[0]

    cursor.execute("select championID from playergame where playerID = %lu" % (playerID))
    gameData = cursor.fetchall()

    matchlistSize = len(gameData)
    championRatios = {}
    for match in gameData: 
        championID = match[0]
        if championRatios.has_key(championID):
            championRatios[championID] += 1.0 / matchlistSize
        else:
            championRatios[championID] = 1.0 / matchlistSize

    serverChampionRatios = _getServerChampionRatios()


    similarityList = {}
    for accountID, playerChampionRatios in serverChampionRatios.iteritems():
        x = []
        y = []
        #begin accumulating data points in form of (x,y) pairs
        for championID in championRatios.keys():
            if str(championID) in playerChampionRatios.keys():
                x.append(championRatios[championID])
                y.append(playerChampionRatios[str(championID)])

        #filter out insignifcant graphs with few points, use linear regression of these points to determine similarity score
        if len(x) > 9 and max(y) > 0.03:
            similarityList[accountID] = linregress(x, y)[2]

    totals = {}
    similaritySums = {}
    for accountID, playerChampionRatios in serverChampionRatios.iteritems():
        if accountID == str(playerID) or accountID not in similarityList.keys():
            continue

        playerSimilarity = similarityList[accountID]

        if playerSimilarity < 0:
            continue

        for championID, proportion in playerChampionRatios.iteritems():
            #only calculate for champions not in user's own pool or in a very low proportion of user's champion pool
            if int(championID) not in championRatios.keys() or (int(championID) in championRatios.keys() and championRatios[int(championID)] < 0.01):
                totals.setdefault(championID, 0)
                totals[championID] += playerSimilarity * playerChampionRatios[str(championID)]
                similaritySums.setdefault(championID, 0)
                similaritySums[championID] += playerSimilarity

    predictedProportions = [(championID, total/similaritySums[championID]) for championID, total in totals.iteritems()]
    predictedProportions.sort(key = lambda x: x[1], reverse = True)
    
    entryCount = 1
    recommendedData = []
    for entry in predictedProportions:
        if entryCount > 10:
            break
        recommendedData.append((matchChamp(int(entry[0])), "%.2f" % (entry[1] * 100)))
        entryCount += 1

    return render_template("recommendChamps.html", recommendedData = recommendedData, summonerName = summonerName)



@app.route("/matchChamp/<championID>")
def matchChamp(championID):
    with open('champion.json') as f:
        champData = json.load(f)
    json_tree = objectpath.Tree(champData['data'])
    result_tuple = tuple(json_tree.execute(("$..*[@.key is %s].id" % championID)))
    for entry in result_tuple:
        return entry

@app.route("/player/<summonerName>", methods=['GET'])
def player(summonerName):
    url = "%ssummoner/v3/summoners/by-name/%s?api_key=%s" % (BASE_URL, summonerName, API_KEY)
    jsonResponse = _request(url)

    if "accountId" in jsonResponse:
        # valid summoner name
        playerID = jsonResponse["accountId"]
        summonerID = jsonResponse["id"]

        cursor.execute("select * from player where playerID = %s" % (playerID))
        playerData = cursor.fetchone()
        
        if playerData == None:
            # user info doesn't exist, add to db
            cursor.execute("insert into player values(%lu, %lu, '%s')" % (playerID, summonerID, summonerName))
            conn.commit()
            print "first time user"

        insertPlayerGames(playerID)

        # cursor.execute("select * from playergame where playerID = %s order by timestamp desc" % (playerID))
        cursor.execute("""\
            select playerID, playergame.gameID, timestamp, championID, championString, lane, kills, deaths, assists
            ,case 
                when (((game.team1Player1ID = playergame.playerID
                    OR game.team1Player2ID = playergame.playerID
                    OR game.team1Player3ID = playergame.playerID
                    OR game.team1Player4ID = playergame.playerID
                    OR game.team1Player5ID = playergame.playerID) AND game.winTeam = 1) OR
                    ((game.team2Player1ID = playergame.playerID
                    OR game.team2Player2ID = playergame.playerID
                    OR game.team2Player3ID = playergame.playerID
                    OR game.team2Player4ID = playergame.playerID
                    OR game.team2Player5ID = playergame.playerID) AND game.winTeam = 2))   then 'Victory'
                else 'Defeat'
            end
            as WinStatus 
            FROM game JOIN playergame ON (game.gameID = playergame.gameID)
            where playergame.playerID = %s order by timestamp desc""" % (playerID))
        gameData = cursor.fetchmany(20)

        return render_template("player.html", gameData = gameData, summonerName = summonerName)
    else:
        # summoner name not found
        return "ERROR: summoner not found (API key probably expired)"

@app.route("/champPool/<summonerName>", methods=['GET'])
def champPool(summonerName):
    player(summonerName);
    cursor.execute("select summonerID from player where summonerName = '%s'" % (summonerName))
    summonerID = cursor.fetchone()[0]
    url = "%schampion-mastery/v3/champion-masteries/by-summoner/%lu?api_key=%s" % (BASE_URL, summonerID, API_KEY)
    jsonResponse = _request(url)
    # print jsonResponse

    count = 0;
    for champ in jsonResponse:
        if count == 30:
            break
        count += 1

        championID = champ["championId"]
        championString = matchChamp(championID)
        championLevel = champ["championLevel"]
        championPoints = champ["championPoints"]

        cursor.execute("select * from champPool where summonerID = %lu and championID = %d" % (summonerID, championID))
        if cursor.fetchone() != None:
            # game already exists in database
            break

        cursor.execute("insert into champPool values(%lu, %lu, '%s', %d, %lu)" 
            % (summonerID, championID, championString, championLevel, championPoints))

        # print "committed " + str(summonerID) + " " + championString
        time.sleep(0.1)
    conn.commit()
    # return "summonerID"
    cursor.execute("select * from champPool where summonerID = %lu order by championPoints desc" % (summonerID))
    champData = cursor.fetchmany(20)

    return render_template("champPool.html", champData = champData, summonerName = summonerName)


@app.route("/delete/<playerID>/<gameID>")
def delete(playerID, gameID):
    cursor.execute("delete from playergame where playerID = %s and gameID = %s" % (playerID, gameID))
    conn.commit()
    return "deleted"

@app.route("/clearAllTables")
def clearAll():
    cursor.execute("delete from game")
    cursor.execute("delete from player")
    cursor.execute("delete from playergame")
    cursor.execute("delete from champPool")
    conn.commit()
    return "Database Cleared"

@app.route("/update/<playerID>/<gameID>/<champID>")
def update(playerID, gameID, champID):
    championString = matchChamp(champID)
    cursor.execute("update playergame SET championID = %s, championString = '%s' WHERE playerID = %s and gameID = %s" % (champID, championString, playerID, gameID))
    conn.commit()
    return "updated"

def insertPlayerGames(playerID):
    url = "%smatch/v3/matchlists/by-account/%s?api_key=%s" % (BASE_URL, playerID, API_KEY)
    jsonResponse = _request(url)

    count = 0
    for game in jsonResponse["matches"]:
        # if count == 20:
        #     break
        count += 1

        gameID = game["gameId"]

        cursor.execute("select * from playergame where playerID = %lu and gameID = %lu" % (playerID, gameID))
        data = cursor.fetchone()
        if data != None:
            # game already exists in database
            break

        # player stats
        timestamp = time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(game["timestamp"]/1000))
        championID = game["champion"]
        championString = matchChamp(championID)

        lane = game["lane"]

        kills = 0
        deaths = 0
        assists = 0

        # team stats
        gameUrl = "%smatch/v3/matches/%s?api_key=%s" % (BASE_URL, gameID, API_KEY)
        gameJsonResponse = _request(gameUrl)

        # error parsing - rate limit exceeded
        if "gameMode" not in gameJsonResponse:
            time.sleep(1)
            continue

        # only parse classic 5v5 games
        if gameJsonResponse["gameMode"] not in VALID_GAME_MODES:
            continue

        gameDuration = gameJsonResponse["gameDuration"]
        queueID = gameJsonResponse["queueId"]
        seasonID = gameJsonResponse["seasonId"]

        winTeam = 1 if gameJsonResponse["teams"][0]["win"] == "Win" else 2

        team1Kills = 0
        team1Deaths = 0
        team1Assists = 0
        team1Gold = 0
        team1TowerKills = gameJsonResponse["teams"][0]["towerKills"]
        team1InhibKills = gameJsonResponse["teams"][0]["inhibitorKills"]
        team1BaronKills = gameJsonResponse["teams"][0]["baronKills"]
        team1DragonKills = gameJsonResponse["teams"][0]["dragonKills"]

        team2Kills = 0
        team2Deaths = 0
        team2Assists = 0
        team2Gold = 0
        team2TowerKills = gameJsonResponse["teams"][1]["towerKills"]
        team2InhibKills = gameJsonResponse["teams"][1]["inhibitorKills"]
        team2BaronKills = gameJsonResponse["teams"][1]["baronKills"]
        team2DragonKills = gameJsonResponse["teams"][1]["dragonKills"]

        playerIDs = [0] * 10
        for i in xrange(len(gameJsonResponse["participantIdentities"])):
            playerIDs[i] = gameJsonResponse["participantIdentities"][i]["player"]["accountId"]

        for i in xrange(len(gameJsonResponse["participants"])):
            participant = gameJsonResponse["participants"][i]
            if participant["teamId"] == 100:
                team1Kills += participant["stats"]["kills"]
                team1Deaths += participant["stats"]["deaths"]
                team1Assists += participant["stats"]["assists"]
                team1Gold += participant["stats"]["goldEarned"]
            else:
                team2Kills += participant["stats"]["kills"]
                team2Deaths += participant["stats"]["deaths"]
                team2Assists += participant["stats"]["assists"]
                team2Gold += participant["stats"]["goldEarned"]

            if playerID == gameJsonResponse["participantIdentities"][i]["player"]["accountId"]:
                kills = participant["stats"]["kills"]
                deaths = participant["stats"]["deaths"]
                assists = participant["stats"]["assists"]

        cursor.execute("select * from game where gameID = %lu" % (gameID))
        data = cursor.fetchone()
        if data == None:
            cursor.execute("insert into game values(%lu,%d,%d,%d,%d, %d,%d,%d,%d,%d,%d,%d,%d, %d,%d,%d,%d,%d,%d,%d,%d, %lu,%lu,%lu,%lu,%lu,%lu,%lu,%lu,%lu,%lu)"
                % (gameID, gameDuration, queueID, seasonID, winTeam,
                    team1Kills, team1Deaths, team1Assists, team1TowerKills, team1InhibKills, team1BaronKills, team1DragonKills, team1Gold,
                    team2Kills, team2Deaths, team2Assists, team2TowerKills, team2InhibKills, team2BaronKills, team2DragonKills, team2Gold,
                    playerIDs[0], playerIDs[1], playerIDs[2], playerIDs[3], playerIDs[4], playerIDs[5], playerIDs[6], playerIDs[7], playerIDs[8], playerIDs[9]))
        
        cursor.execute("insert into playergame values(%lu, %lu, '%s', %d, '%s', '%s', %d, %d, %d)" 
            % (playerID, gameID, timestamp, championID, championString, lane, kills, deaths, assists))

        print "committed " + str(gameID)
        time.sleep(0.1)

    conn.commit()



def _request(url):
    response = requests.get(url)
    return response.json()


if __name__ == "__main__":
    app.run()