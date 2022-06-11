import spotipy as sp
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from .SongEntry import SongEntry

class InvalidSearchError(Exception):
    pass


class SpotifyHandler:
    def __init__(self, scope, account_info):
        self.__device_id = None
        self.__device_name = None
        self.__spotify = None
        self.__scope = scope
        self.__account_info = account_info
        redirect_uri = 'http://localhost:6400/callback'
        auth_manager = self.__create_auth_manager(account_info, self.__scope, redirect_uri)
        self.__spotify = sp.Spotify(auth_manager=auth_manager)
        self.__set_device_id()

    @staticmethod
    def __create_auth_manager(account_file, scope, redirect_uri) -> object:
        """
        Reads in account data from the specified file and creates an Authentication Manager object
        :param account_file: file holding the account information
        :return auth_manager: Created Authentication Manager
        """
        load_dotenv(account_file)
        return SpotifyOAuth(client_id=os.environ.get('CLIENT_ID'),
                            client_secret=os.environ.get('CLIENT_SECRET'),
                            redirect_uri=redirect_uri,
                            scope=scope,
                            username=os.environ.get('USERNAME'))
    
    def __set_device_id(self):
        devices = self.__spotify.devices()
        load_dotenv(self.__account_info)
        for d in devices['devices']:
            d['name'] = d['name'].replace('’', '\'')
            if d['name'] == os.environ.get("DEVICE_NAME"):
                self.deviceID = d['id']
                return
            if d['name'] == os.environ.get("ALT_DEVICE_NAME"):
                self.deviceID = d['id']
                return
            if d['name'] == os.environ.get("ALT_DEVICE_NAME_2"):
                self.deviceID = d['id']
                return

    def update_device(self):
        self.__set_device_id()


    def get_track_artist(self):
        try:
            return self.get_song()['artists'][0]['name']
        except:
            return None


    def get_track_name(self):
        try:
            return self.get_song()['name']
        except:
            return None


    def get_track_uri(self):
        try:
            return self.get_song()['uri']
        except:
            return None


    def get_name_artist_uri(self):
        try:
            _song = self.get_song()
            name = _song['name']
            artist = _song['artists'][0]['name']
            uri = _song['uri']
        except:
            return None, None, None
        return name, artist, uri


    def get_ms(self):
        try:
            return self.__spotify.currently_playing()['progress_ms']
        except:
            return None


    def get_album_uri(self, name: str) -> str:
        """
        :param spotify: Spotify object to make the search from
        :param name: album name
        :return: Spotify uri of the desired album
        """

        # Replace all spaces in name with '+'
        original = name
        name = name.replace(' ', '+')

        results = self.__spotify.search(q=name, limit=1, type='album')
        if not results['albums']['items']:
            raise InvalidSearchError(f'No album named "{original}"')
        album_uri = results['albums']['items'][0]['uri']
        return album_uri


    def get_artist_uri(self, name: str) -> str:
        """
        :param spotify: Spotify object to make the search from
        :param name: album name
        :return: Spotify uri of the desired artist
        """

        # Replace all spaces in name with '+'
        original = name
        name = name.replace(' ', '+')

        results = self.__spotify.search(q=name, limit=1, type='artist')
        if not results['artists']['items']:
            raise InvalidSearchError(f'No artist named "{original}"')
        artist_uri = results['artists']['items'][0]['uri']
        print(results['artists']['items'][0]['name'])
        return artist_uri


    def get_track_uri_by_name(self, name: str, artist: str = None) -> str:
        """
        :param artist: artist name
        :param spotify: Spotify object to make the search from
        :param name: track name
        :return: Spotify uri of the desired track
        """

        # Replace all spaces in name with '+'
        original = name
        name = name.replace(' ', '+')
        results = self.__spotify.search(q=name, limit=50, type='track')
        track_uri = ''
        if artist is None:
            if not results['tracks']['items']:
                raise InvalidSearchError(f'No track named "{original}"')
            track_uri = results['tracks']['items'][0]['uri']
            return track_uri
        else:
            for item in results['tracks']['items']:
                if artist in item['artists'][0]['name'].lower():
                    track_uri = item['uri']
                    break
            if not results['tracks']['items']:
                raise InvalidSearchError(f'No track named "{original}"')
            return track_uri


    def get_track_info(self, name: str, artist: str = None):
        name = name.replace(' ', '+')
        results = self.__spotify.search(q=name, limit=50, type='track')
        for item in results['tracks']['items']:
            if artist in item['artists'][0]['name'].lower():
                track = item
                break
        return track


    def play_artist(self, uri=None):
        self.__spotify.start_playback(device_id=self.__device_id, context_uri=uri)


    def play_track(self, uri=None):
        self.__spotify.start_playback(device_id=self.__device_id, uris=[uri])


    def play_album(self, uri=None):
        self.__spotify.start_playback(device_id=self.__device_id, context_uri=uri)


    def add_to_queue(self, uri: None):
        self.__spotify.add_to_queue(uri=uri, device_id=self.__device_id)


    def pause_song(self):
        self.__spotify.pause_playback(device_id=self.__device_id)


    def continue_song(self):
        self.__spotify.start_playback(device_id=self.__device_id)


    def add_song(self):
        uri = self.__spotify.currently_playing()['item']['uri']
        self.__spotify.current_user_saved_tracks_add([uri])


    def get_song(self):
        return self.__spotify.currently_playing()['item']
    
    
    def get_song_info(self):
        _song = self.__spotify.currently_playing()['item']
        print(_song)
        name = _song['name']
        artist = _song['artists'][0]['name']
        uri = _song['uri']
        album = _song['album']['name']
        popularity = _song['popularity']
        duration = _song['duration_ms']
        img_src = _song['album']['images'][0]['url']
        return SongEntry(name, artist, uri, album, popularity, duration, img_src)


    def play_saved(self):
        self.__spotify.start_playback(device_id=self.__device_id, context_uri=spotify.current_user_saved_tracks())


    def get_playlist_uri(self, name: str) -> str:
        pl_uri = ''
        result = self.__spotify.current_user_playlists(limit=50)
        result2 = self.__spotify.playlist
        for item in result['items']:
            if name in item['name'].lower():
                pl_uri = item['uri']
                break
        if pl_uri == '':
            raise InvalidSearchError(f'No playlist named "{name}"')
        return pl_uri


    def play_playlist(self, uri=None):
        self.__spotify.start_playback(device_id=self.__device_id, context_uri=uri)
        

    def add_to_playlist(self, uris: [], pl_name):
        """
        adds given uris to the given playlist if theyre not already in there
        :param uris: uris to add
        :param pl_name: playlist name
        """
        pl_uri = self.get_playlist_uri(pl_name)
        res = self.__spotify.playlist_items(pl_uri)
        items = res['items']
        print('[Spotify] Lieder: ', len(items))
        songs = list(map(lambda item: item['track']['uri'], items))

        to_remove = []
        for i in range(len(uris)):
            if uris[i] in songs:
                to_remove.append(uris[i])
        for uri in to_remove:
            uris.remove(uri)
        if len(uris) > 0:
            self.__spotify.playlist_add_items(pl_uri, uris)
        logging.info(f'\n\n[Spotify] Action: Added {len(uris)} to {pl_name}')

    def add_to_playlist_without_check(self, uris: [], pl_name):
        pl_uri = self.get_playlist_uri(pl_name)
        self.__spotify.playlist_add_items(pl_uri, uris)

    def empty_playlist(self, pl_name):
        """
        deletes the playlist named general
        :param pl_name: playlist to delete
        """
        pl_uri = self.get_playlist_uri(pl_name)
        res = self.__spotify.playlist_items(pl_uri)
        items = res['items']
        songs = list(map(lambda item: item['track']['uri'], items))
        self.__spotify.playlist_remove_all_occurrences_of_items(pl_uri, songs)
        logging.info(f'\n\n[Spotify] Deleted: {pl_name}')

    def set_playlist(self, uris, pl_name):
        """
        fills the playlist named general with the given uris
        :param pl_name: playlist to fill
        :param uris: uris to use
        """
        logging.info(f'\n\n[Spotify] Action: Setting {pl_name}')
        self.empty_playlist(pl_name)
        self.add_to_playlist_without_check(uris, pl_name)
        logging.info(f'\n\n[Spotify] Created: {pl_name} set')
