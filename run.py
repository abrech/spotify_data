import schedule
import time
import math
import requests
import traceback
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request
from flask_cors import CORS
import atexit
import json
from classes.SpotifyHandler import SpotifyHandler
from classes.SpotifyDatabase import SpotifyDatabase
from classes.SongCollector import SongCollector
from classes.SongEvaluator import SongEvaluator
from classes.Logger import Logger


lg = Logger('spotify.log', 'spotify_error.log')
sp = SpotifyHandler(lg, 'user-read-private user-read-playback-state user-modify-playback-state user-library-modify playlist-read-private playlist-modify-private playlist-modify-public', 'account.env')
db = SpotifyDatabase(lg)
cl = SongCollector(sp, db, lg, 10)
ev = SongEvaluator(sp, db, lg)
tmp = 0

dc_count = 0
def run_collector():
    global tmp
    cl.run()

def eval_all(recursive_count=0):
    try:
        ev.evaluate_all('all', 30)
        # ev.evaluate_genres('all', ['pop', 'dance pop'], 30)
        # ev.evaluate_popularity_songs('all', 1, 1000, 30)
    except TimeoutError:
        lg.log("RUN "+traceback.format_exc(), 1)
        time.sleep(30)
        if recursive_count < 3:
            recursive_count += 1
            eval_all(recursive_count)

def eval_period():
    ev.evaluate_period('4week', 28, 25)
    ev.evaluate_period('2week', 14, 20)

# schedule.every(4).seconds.do(run_collector)
# schedule.every(20).seconds.do(eval_all)
# schedule.every().day.at("04:00").do(eval_all)

lg.log("RUN Checking database...", 0)
songs = db.execute_select("select * from songs;")
song = str(songs[0]).encode('utf-8') if len(songs) > 0 else "Empty"
lg.log(f"RUN {len(songs)} entries: "+str(song), 0)
lg.log("RUN Check successful.", 0)

#"""
sched = BackgroundScheduler(daemon=True)
sched.add_job(eval_all,'cron', hour='2', minute='30')
sched.add_job(eval_period,'cron', hour='3', minute='30')
sched.add_job(run_collector,'interval', seconds=10)
# sched.add_job(eval_all,'interval', seconds=20)
sched.start()


app = Flask(__name__)
CORS(app)

@app.route("/")
def arduino():
    return "Hallotest"


@app.route("/test")
def test():
    return "Hallotest"

# arduino stuff
@app.route("/discord/set/<count>")
def set_discord_count(count):
    if count[:3] == "___":
        count = count[3:]
        global dc_count
        dc_count = int(count)
        return "OK", 200
    return "ERROR"

@app.route("/discord/get")
def get_discord_count():
    global dc_count
    return str(dc_count)

@app.route("/spotify/playing")
def get_spotify_playing():
    try:
        _song = sp.currently_playing()
        name = _song['name']
        artist = _song['artists'][0]['name']
        return f"{name} by {artist}"
    except:
        return "ERROR"

@app.route("/spotify/top")
def get_top_single():
    songs = db.get_most_played_songs(1)
    song = songs[0][1]
    played = songs[0][-1]
    return f"{song} x{played}"

@app.route("/weather/temp/<apikey>/<city>")
def get_temp(apikey, city):
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
    CITY = city
    API_KEY = apikey
    URL = BASE_URL + "q=" + CITY + "&appid=" + API_KEY + "&units=metric"
    response = requests.get(URL)
    # checking the status code of the request
    if response.status_code == 200:
        # getting data in the json format
        data = response.json()
        desc = data['weather'][0]['description']
        temp = data['main']['temp']
        max_temp = data['main']['temp_max']

        return f"Temp {round(temp)}C Max {round(max_temp)}C\n{desc}"
    return "ERROR"

# end

@app.route("/get_top_uris/<limit>")
def get_top_uris(limit):
    limit = int(limit)
    return json.dumps({'uris': db.get_most_played_uris(limit)}), 200, {'ContentType': 'application/json'}

@app.route("/get_top_songs/<limit>")
def get_top_songs(limit):
    limit = int(limit)
    return json.dumps({'songs': db.get_most_played_songs(limit)}), 200, {'ContentType': 'application/json'}

@app.route("/get_genres")
def get_genres():
    genres = db.get_genres()
    genres.sort()
    return json.dumps({'genres': genres}), 200, {'ContentType': 'application/json'}
    
@app.route("/get_songs_by_genres")
def get_songs_by_genres():
    args = request.args
    genres = args.get('genres').split(" ")
    return json.dumps({'songs': db.get_most_played_by_genres(genres, 30)}), 200, {'ContentType': 'application/json'}
    
# Shut down the scheduler when exiting the app
atexit.register(lambda: sched.shutdown())

if __name__ == "__main__":
    eval_period()
    app.run(host='0.0.0.0', port=6400, use_reloader=False)
"""
# checks pending schedules
while True:
    time.sleep(1)
    try:
        schedule.run_pending()
    except TimeoutError:
        lg.log("RUN "+traceback.format_exc(), 1)
    except Exception as ex:
        lg.log("RUN "+traceback.format_exc(), 2)
        raise
"""

