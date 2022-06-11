import schedule
import time
from datetime import datetime
from classes.SpotifyHandler import SpotifyHandler
from classes.SpotifyDatabase import SpotifyDatabase
from classes.SongCollector import SongCollector


sp = SpotifyHandler('user-read-private user-read-playback-state user-modify-playback-state user-library-modify playlist-read-private playlist-modify-private playlist-modify-public', 'account.env')
db = SpotifyDatabase()
cl = SongCollector(sp, db, 10)

def run_collec():
    cl.run_collector()

# setting schedules
schedule.every(4).seconds.do(run_collec)


# checks pending schedules
while True:
    schedule.run_pending()
    time.sleep(1)