import schedule
import time
from datetime import datetime
from classes.SpotifyHandler import SpotifyHandler
from classes.SpotifyDatabase import SpotifyDatabase
from classes.SongCollector import SongCollector
from classes.SongEvaluator import SongEvaluator


sp = SpotifyHandler('user-read-private user-read-playback-state user-modify-playback-state user-library-modify playlist-read-private playlist-modify-private playlist-modify-public', 'account.env')
db = SpotifyDatabase()
cl = SongCollector(sp, db, 4)
ev = SongEvaluator(sp, db)

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

for entry in db.execute_select("select * from songs;"):
    print(str(entry).encode('utf-8'))
# checks pending schedules
while True:
    schedule.run_pending()
    time.sleep(1)

