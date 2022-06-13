
class SongEntry:
    def __init__(self, song, artist, uri, album, popularity, duration, img_src):
        self.song = song
        self.artist = artist
        self.uri = uri
        self.album = album
        self.popularity = popularity
        self.duration = duration
        self.img_src = img_src
    
    def __str__(self) -> str:
        return f"Added {self.song} by {self.artist}"
    
        