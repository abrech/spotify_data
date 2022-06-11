
class SongEvaluator:
    def __init__(self, db, sp):
        self.__db = db
        self.__spotify = sp
        
    def get_most_played(self, limit=40):
        return self.__db.get_most_played_uris(limit)

    def evaluate_all(self, pl_name, limit=40):
        most_played = self.get_most_played(limit)
        self.__spotify.set_playlist(most_played, pl_name)
    
    def evaluate_period(self):
        pass
        