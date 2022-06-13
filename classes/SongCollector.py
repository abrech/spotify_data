import requests
import traceback
from .Logger import Logger
from .SpotifyHandler import SpotifyHandler
from .SpotifyDatabase import SpotifyDatabase

class SongCollector:
    def __init__(self, spotify: SpotifyHandler, database: SpotifyDatabase, logger: Logger, min_time_played):
        self.__logger = logger
        self.__spotify = spotify
        self.__db = database
        self.__min_time_played = min_time_played * 1000
        self.__previous_uri = None
    
    
    def collect(self):
        try:
            song_obj = self.__spotify.get_song_info()
        except requests.exceptions.ReadTimeout as ex:
            self.__logger.log("COLL "+traceback.format_exc(), level=1)

        if not song_obj.uri or song_obj.uri == self.__previous_uri:
            return
        
        self.__previous_uri = song_obj.uri
        self.__db.add_song(song_obj)
    
    def run(self):
        ms = self.__spotify.get_ms()
        if ms and ms > self.__min_time_played:
            self.collect()
        elif not ms:
            self.__spotify.update_device()
