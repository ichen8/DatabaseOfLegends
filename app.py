#!/usr/local/bin/python2.7
# https://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972

from flask import Flask, render_template
from flaskext.mysql import MySQL
from pprint import pprint

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

API_KEY = "RGAPI-64ffe71a-480f-402b-bfc3-41c8e5ac0f39"
BASE_URL = "https://na1.api.riotgames.com/lol/"

VALID_GAME_MODES = ["CLASSIC", "ARAM"]

@app.route("/")
def index():
    return "Welcome!"

@app.route("/matchChamp/<championID>")
def matchChamp(championID):
    with open('champion.json') as f:
        champData = json.load(f)
    json_tree = objectpath.Tree(champData['data'])
    result_tuple = tuple(json_tree.execute(("$..*[@.key is %s].name" % championID)))
    for entry in result_tuple:
        return entry

@app.route("/player/<summonerName>")
def player(summonerName):
    url = "%ssummoner/v3/summoners/by-name/%s?api_key=%s" % (BASE_URL, summonerName, API_KEY)
    jsonResponse = _request(url)

    if "accountId" in jsonResponse:
        # valid summoner name
        playerID = jsonResponse["accountId"]

        cursor.execute("select * from player where playerID = %s" % (playerID))
        playerData = cursor.fetchone()
        
        if playerData == None:
            # user info doesn't exist, add to db
            cursor.execute("insert into player values(%lu, '%s')" % (playerID, summonerName))
            conn.commit()
            print "first time user"

        insertPlayerGames(playerID)

        cursor.execute("select * from playergame where playerID = %s order by timestamp desc" % (playerID))
        gameData = cursor.fetchmany(10)

        return render_template("index.html", gameData = gameData)
    else:
        # summoner name not found
        return "ERROR: summoner not found"

@app.route("/delete/<playerID>/<gameID>")
def delete(playerID, gameID):
    cursor.execute("delete from playergame where playerID = %s and gameID = %s" % (playerID, gameID))
    conn.commit()
    return "deleted"

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
        if count == 20:
            break
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

        team1Player1ID = gameJsonResponse["participantIdentities"][0]["player"]["accountId"]
        team1Player2ID = gameJsonResponse["participantIdentities"][1]["player"]["accountId"]
        team1Player3ID = gameJsonResponse["participantIdentities"][2]["player"]["accountId"]
        team1Player4ID = gameJsonResponse["participantIdentities"][3]["player"]["accountId"]
        team1Player5ID = gameJsonResponse["participantIdentities"][4]["player"]["accountId"]
        team2Player1ID = gameJsonResponse["participantIdentities"][5]["player"]["accountId"]
        team2Player2ID = gameJsonResponse["participantIdentities"][6]["player"]["accountId"]
        team2Player3ID = gameJsonResponse["participantIdentities"][7]["player"]["accountId"]
        team2Player4ID = gameJsonResponse["participantIdentities"][8]["player"]["accountId"]
        team2Player5ID = gameJsonResponse["participantIdentities"][9]["player"]["accountId"]

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
                    team1Player1ID, team1Player2ID, team1Player3ID, team1Player4ID, team1Player5ID, team2Player1ID, team2Player2ID, team2Player3ID, team2Player4ID, team2Player5ID))
        
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