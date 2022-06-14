import schedule
import time
import traceback
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
import atexit
from classes.SpotifyHandler import SpotifyHandler
from classes.SpotifyDatabase import SpotifyDatabase
from classes.SongCollector import SongCollector
from classes.SongEvaluator import SongEvaluator
from classes.Logger import Logger


lg = Logger('spotify.log', 'spotify_error.log')
sp = SpotifyHandler(lg, 'user-read-private user-read-playback-state user-modify-playback-state user-library-modify playlist-read-private playlist-modify-private playlist-modify-public', 'account.env')
db = SpotifyDatabase(lg)
cl = SongCollector(sp, db, lg, 20)
ev = SongEvaluator(sp, db, lg)

def run_collector():
    cl.run()

def eval_all(recursive_count=0):
    try:
        # ev.evaluate_all('all', 30)
        # ev.evaluate_genres('all', ['pop', 'dance pop'], 30)
        ev.evaluate_popularity_songs('all', 1, 1000, 30)
    except TimeoutError:
        lg.log("RUN "+traceback.format_exc(), 1)
        time.sleep(30)
        if recursive_count < 3:
            recursive_count += 1
            eval_all(recursive_count)

def eval_period():
    ev.evaluate_period('4week', 28, 30)

# schedule.every(4).seconds.do(run_collector)
# schedule.every(20).seconds.do(eval_all)
# schedule.every().day.at("04:00").do(eval_all)

res = db.execute_select("select * from songs;")
for r in res:
    print(r)

lg.log("RUN Checking database...", 0)
songs = db.execute_select("select * from songs;")
song = str(songs[0]).encode('utf-8') if len(songs) > 0 else "Empty"
lg.log(f"RUN {len(songs)} entries: "+str(song), 0)
lg.log("RUN Check successful.", 0)

print(db.execute_select("select * from artists;"))
print(db.execute_select("select * from artists_genres;"))

#"""
sched = BackgroundScheduler(daemon=True)
# sched.add_job(eval_all,'cron', hour='2', minute='30')
sched.add_job(run_collector,'interval', seconds=5)
sched.add_job(eval_all,'interval', seconds=20)
sched.start()

app = Flask(__name__)

@app.route("/home")
def home():
    """ Function for test purposes. """
    global gl
    gl += 1
    return "Welcome Home :) !"

# Shut down the scheduler when exiting the app
atexit.register(lambda: sched.shutdown())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6400)
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

