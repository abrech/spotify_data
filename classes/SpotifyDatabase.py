import sqlite3 as sql

from .ArtistEntry import ArtistEntry
from .SongEntry import SongEntry
import time
import math
from datetime import datetime, timedelta, timezone
from .Logger import Logger

class SpotifyDatabase:
    def __init__(self, logger: Logger):
        self.__logger = logger
        self.__connection = sql.connect("spotifysongs.db", check_same_thread=False)
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
                              "(uri TEXT not null primary key, song TEXT, artist TEXT, artist_uri TEXT, "
                              "album TEXT, popularity INTEGER, duration INTEGER, img_src TEXT, times_played INTEGER);")
        self.__cursor.execute("create table songs_times (song_uri TEXT, datetime INTEGER);")
        self.__cursor.execute("create table artists (artist_uri TEXT not null primary key, name TEXT, popularity INTEGER);")
        self.__cursor.execute("create table artists_genres (artist_uri TEXT, genre TEXT);")

    def execute_select(self, statement):
        return self.__cursor.execute(statement).fetchall()

    def add_song(self, song_obj: SongEntry):
        #statement = f"insert into songs values ('{song_obj.uri}', '{song_obj.song}', '{song_obj.artist}', '{song_obj.album}'," \
        #            f"{song_obj.popularity}, {song_obj.duration}, '{song_obj.img_src}', {1}) " \
        #            f"on conflict(uri) do update set times_played=times_played+1;"
        res = self.__cursor.execute(f"select uri from songs where uri like '{song_obj.uri}';").fetchall()
        before_res = len(res)
        statement = f"insert or ignore into songs values ('{song_obj.uri}', '{song_obj.song}', '{song_obj.artist}', '{song_obj.artist_uri}', '{song_obj.album}'," \
                    f"{song_obj.popularity}, {song_obj.duration}, '{song_obj.img_src}', {0});"
        self.__cursor.execute(statement)
        res = self.__cursor.execute(f"select uri from songs where uri like '{song_obj.uri}';").fetchall()
        after_res = len(res)
        update = f"update songs set times_played = times_played + 1 where uri like '{song_obj.uri}';"
        self.__cursor.execute(update)

        epoch_time = int(time.time())
        insert = f"insert into songs_times values('{song_obj.uri}', {epoch_time});"
        self.__cursor.execute(insert)
        self.__commit()
        
        if before_res < after_res:
            self.__logger.log("DB Added "+str(song_obj))
    
    def add_artist(self, artist_obj: ArtistEntry):
        statement = f"insert or ignore into artists values('{artist_obj.uri}', '{artist_obj.name}', {artist_obj.popularity});"
        self.__cursor.execute(statement)
        artist_in_genres = self.__cursor.execute(f"select count(artist_uri) from artists_genres where artist_uri like '{artist_obj.uri}';").fetchall()
        artist_count = artist_in_genres[0][0]
        
        if artist_count > 0:
            self.__commit()
            return
        
        artist_log = f"DB Added {str(artist_obj)}, genres"
        for genre in artist_obj.genres:
            insert_genre = f"insert into artists_genres values('{artist_obj.uri}', '{genre}');"
            self.__cursor.execute(insert_genre)
            artist_log += f" - {genre}"
        artist_obj = str(artist_obj) + ": Empty" if len(artist_obj.genres) < 1 else artist_obj
        self.__logger.log(artist_log, 0)
        self.__commit()
    
    def get_most_played_uris(self, limit: int):
        statement = f"select uri from songs order by times_played desc;"
        uris = self.__cursor.execute(statement).fetchall()
        uris_limited = uris[:limit]
        out = [uri[0] for uri in uris_limited]
        return out
    
    def get_most_played_songs(self, limit: int):
        statement = f"select * from songs order by times_played desc;"
        uris = self.__cursor.execute(statement).fetchall()
        out = uris[:limit]
        return out
    
    def get_most_played_in_period(self, days, limit):
        time_start = math.floor((datetime.now(timezone.utc) - timedelta(days)).timestamp())
        statement = f"select s.uri, count(t.song_uri) as times from songs s join songs_times t on s.uri = t.song_uri where t.datetime > {time_start} group by s.uri order by times desc;"
        uris = self.__cursor.execute(statement).fetchall()
        uris_limited = uris[:limit]
        out = [uri[0] for uri in uris_limited]
        return out

    def get_most_played_by_genres(self, genres: list, limit):
        if len(genres) < 1:
            return self.get_most_played_uris(limit)
        
        genre_str = f"genre like '{genres[:1][0]}'"
        for genre in genres[1:]:
            genre_str += f" or genre like '{genre}'"
        print(genre_str)
        statement = f"select distinct s.uri, s.song, s.artist, s.artist_uri, s.album, s.popularity, s.duration, s.img_src, s.times_played from songs s join artists_genres g on s.artist_uri = g.artist_uri where {genre_str} order by s.times_played desc;"
        uris = self.__cursor.execute(statement).fetchall()
        uris_limited = uris[:limit]
        out = [uri[0] for uri in uris_limited]
        return out
    
    def get_most_played(self, limit=30, **kwargs):
        pre = f"select distinct s.uri from songs s"
        post = f" order by s.times_played desc"
        statement = ""
        genre_str = ""
        if "genres" in kwargs and len(kwargs["genres"]) >= 1:
            genres = kwargs["genres"]
            genre_str = f"g.genre like '{genres[:1][0]}'"
            for genre in genres[1:]:
                genre_str += f" or g.genre like '{genre}'"
            statement += f" join artists_genres g on s.artist_uri = g.artist_uri "
        if "days" in kwargs:
            pre = "select s.uri, count(t.song_uri) as times from songs s "
            post = f" order by times desc;"
            time_start = math.floor((datetime.now(timezone.utc) - timedelta(int(kwargs["days"]))).timestamp())
            if len(genre_str) > 1:
                statement += f" join songs_times t on s.uri = t.song_uri where t.datetime > {time_start} and ({genre_str}) group by s.uri "
            else:
                statement += f" join songs_times t on s.uri = t.song_uri where t.datetime > {time_start} group by s.uri "
                
        elif len(genre_str) > 1:
            statement += f" where {genre_str} "
        res = pre + statement + post
        print(res)
        uris = self.__cursor.execute(res).fetchall()
        uris_limited = uris[:limit]
        out = [uri[0] for uri in uris_limited]
        return out

    def get_most_played_by_song_popularity(self, min_popularity, max_popularity, limit):
        statement = f"select * from songs where popularity <= {max_popularity} and popularity >= {min_popularity} order by times_played desc;"
        uris = self.__cursor.execute(statement).fetchall()
        uris_limited = uris[:limit]
        out = [uri[0] for uri in uris_limited]
        return out
    
    def get_genres(self):
        statement = f"select distinct genre from artists_genres;"
        genres = self.__cursor.execute(statement).fetchall()
        out = [genre[0] for genre in genres]
        return out
        