from .Logger import Logger


class SongEvaluator:
    def __init__(self, sp, db, logger: Logger):
        self.__logger = logger
        self.__db = db
        self.__spotify = sp
        
    def get_most_played(self, limit):
        return self.__db.get_most_played_uris(limit)

    def evaluate_all(self, pl_name, limit):
        most_played = self.get_most_played(limit)
        self.__spotify.set_playlist(most_played, pl_name)
        self.__logger(f"Set playlist '{pl_name}'")
    
    def evaluate_period(self, pl_name, days, limit):
        most_played = self.__db.get_most_played_in_period(days, limit)
        self.__spotify.set_playlist(most_played, pl_name)
        self.__logger(f"Set playlist '{pl_name}'")
        