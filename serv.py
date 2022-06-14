from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
import atexit

gl = 0

def sensor():
    global gl
    """ Function for test purposes. """
    print(f"{gl} Scheduler is alive!")

sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor,'cron', hour='2', minute='30')
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
    app.run(port=6400)