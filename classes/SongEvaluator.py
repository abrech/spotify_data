from classes.SpotifyDatabase import SpotifyDatabase
from classes.SpotifyHandler import SpotifyHandler
from .Logger import Logger


class SongEvaluator:
    def __init__(self, sp: SpotifyHandler, db: SpotifyDatabase, logger: Logger):
        self.__logger = logger
        self.__db = db
        self.__spotify = sp
        
    def get_most_played(self, limit):
        return self.__db.get_most_played_uris(limit)

    def evaluate_all(self, pl_name, limit):
        most_played = self.get_most_played(limit)
        self.__spotify.set_playlist(most_played, pl_name)
        self.__logger.log(f"EVAL Set playlist '{pl_name}'")
    
    def evaluate_period(self, pl_name, days, limit):
        most_played = self.__db.get_most_played_in_period(days, limit)
        self.__spotify.set_playlist(most_played, pl_name)
        self.__logger.log(f"EVAL Set playlist '{pl_name}'")
    
    def evaluate_genres(self, pl_name, genres: list, limit):
        most_played = self.__db.get_most_played_by_genres(genres, limit)
        self.__spotify.set_playlist(most_played, pl_name)
        self.__logger.log(f"EVAL Set playlist '{pl_name}'")
        
    def evaluate_popularity_songs(self, pl_name, min_popularity, max_popularity, limit):
        most_played = self.__db.get_most_played_by_song_popularity(min_popularity, max_popularity, limit)
        self.__spotify.set_playlist(most_played, pl_name)
        self.__logger.log(f"EVAL Set playlist '{pl_name}'")
        