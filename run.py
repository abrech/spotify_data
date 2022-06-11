import schedule
import time
from datetime import datetime
from classes.SpotifyHandler import SpotifyHandler
from classes.SpotifyDatabase import SpotifyDatabase
from classes.SongCollector import SongCollector
from classes.SongEvaluator import SongEvaluator


sp = SpotifyHandler('user-read-private user-read-playback-state user-modify-playback-state user-library-modify playlist-read-private playlist-modify-private playlist-modify-public', 'account.env')
db = SpotifyDatabase()
cl = SongCollector(sp, db, 40)
ev = SongEvaluator(sp, db)


def run_collector():
    cl.run()

def eval_all():
    ev.evaluate_all('all', 30)
    eval_period()

def eval_period():
    ev.evaluate_period('4week', 28, 30)

schedule.every(40).seconds.do(run_collector)
schedule.every().day.at("04:00").do(eval_all)

# checks pending schedules
while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as ex:
        with open('error.log', 'a+') as f:
            f.write(str(ex)+"\n")
