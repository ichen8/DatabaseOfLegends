# https://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972

from flask import Flask, render_template
from flaskext.mysql import MySQL

import json
import requests

app = Flask(__name__)
mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'newpass'
app.config['MYSQL_DATABASE_DB'] = 'lol'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

API_KEY = "RGAPI-338f4df9-5869-4219-979f-6dd191b8c855"
BASE_URL = "https://na1.api.riotgames.com/lol/"

@app.route("/")
def index():
    # cursor.execute("insert into player(playerID, summonerName, timestamp) values(236653651, 'jjjbu', 1540852334000)")
    # conn.commit()
    # print "committed"

    cursor.execute("SELECT * from player")
    data = cursor.fetchone()
    print data
    return "Welcome!"

@app.route("/player/<summonerName>")
def player(summonerName):
    url = "%ssummoner/v3/summoners/by-name/%s?api_key=%s" % (BASE_URL, summonerName, API_KEY)
    jsonResponse = _request(url)

    if "accountId" in jsonResponse:
        # valid summoner name
        playerID = jsonResponse["accountId"]

        cursor.execute("select * from player where playerID = %s" % (playerID))
        data = cursor.fetchone()
        
        if data == None:
            # user info doesn't exist, add to db
            cursor.execute("insert into player values(%d, '%s', 0)" % (playerID, summonerName))
            conn.commit()
            print "first time user"


        return str(playerID)
    else:
        # summoner name not found
        return "ERROR: summoner not found"

def insertPlayerGames(playerID):
    


def _request(url):
    response = requests.get(url)
    return response.json()


if __name__ == "__main__":
    app.run()