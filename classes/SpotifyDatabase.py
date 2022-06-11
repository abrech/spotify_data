import sqlite3 as sql
from .SongEntry import SongEntry
import time

class SpotifyDatabase:
    def __init__(self):
        self.__connection = sql.connect("spotifysongs.db")
        self.__cursor = self.__get_cursor()

        tables = self.__cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        print(tables)
        if len(tables) <= 0:
            self.__create_tables()


    def __commit(self):
        self.__connection.commit()

    def __get_cursor(self):
        return self.__connection.cursor()

    def __create_tables(self):
        self.__cursor.execute("CREATE TABLE songs "
                              "(uri TEXT not null primary key, song TEXT, artist TEXT, "
                              "album TEXT, popularity INTEGER, duration INTEGER, img_src TEXT, times_played INTEGER);")
        self.__cursor.execute("create table times (song_uri TEXT, datetime INTEGER);")

    def execute_select(self, statement):
        return self.__cursor.execute(statement).fetchall()

    def add_song(self, song_obj: SongEntry):
        statement = f"insert into songs values ('{song_obj.uri}', '{song_obj.song}', '{song_obj.artist}', '{song_obj.album}'," \
                    f"{song_obj.popularity}, {song_obj.duration}, '{song_obj.img_src}', {1}) " \
                    f"on conflict(uri) do update set times_played=times_played+1;"
        self.__cursor.execute(statement)

        epoch_time = int(time.time())
        insert = f"insert into times values('{song_obj.uri}', {epoch_time});"
        self.__cursor.execute(insert)
        self.__commit()
    
    def get_most_played_uris(self, limit):
        statement = f"select uri from songs order by times_played desc;"
        uris = self.__cursor.execute(statement).fetchall()
        uris_limited = uris[:limit]
        out = [uri[0] for uri in uris_limited]
        return out
    
