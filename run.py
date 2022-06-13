import schedule
import time
import traceback
from datetime import datetime
from classes.SpotifyHandler import SpotifyHandler
from classes.SpotifyDatabase import SpotifyDatabase
from classes.SongCollector import SongCollector
from classes.SongEvaluator import SongEvaluator
from classes.Logger import Logger


lg = Logger('spotify.log', 'spotify_error.log')
sp = SpotifyHandler(lg, 'user-read-private user-read-playback-state user-modify-playback-state user-library-modify playlist-read-private playlist-modify-private playlist-modify-public', 'account.env')
db = SpotifyDatabase(lg)
cl = SongCollector(sp, db, lg, 4)
ev = SongEvaluator(sp, db, lg)

def run_collector():
    cl.run()

def eval_all():
    ev.evaluate_all('all', 30)
    eval_period()

def eval_period():
    ev.evaluate_period('4week', 28, 30)

schedule.every(4).seconds.do(run_collector)
schedule.every(120).seconds.do(eval_all)
schedule.every().day.at("04:00").do(eval_all)

lg.log("RUN Checking database...", 0)
songs = db.execute_select("select * from songs;")
song = str(songs[0]).encode('utf-8')
lg.log(f"{len(songs)} entries: "+str(song), 0)
lg.log("RUN Check successful.", 0)

# checks pending schedules
while True:
    time.sleep(1)
    try:
        schedule.run_pending()
    except Exception as ex:
        lg.log("RUN "+traceback.format_exc(), 2)
        raise

