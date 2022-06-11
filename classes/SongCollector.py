from .SpotifyHandler import SpotifyHandler

class SongCollector:
    def __init__(self, spotify: SpotifyHandler, min_time_played):
        self.__spotify = spotify
        self.__min_time_played = min_time_played * 1000
    
    
    def collect(self):
        song, artist, uri = self.__spotify.get_name_artist_uri()
        
        
    
    def run_collector(self):
        try:
            ms = self.__spotify.get_ms()
            if ms and ms > self.__min_time_played:
                self.collect()
            elif not ms:
                self.__spotify.update_device()
        except:
            pass