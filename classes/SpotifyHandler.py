import spotipy as sp
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv


class SpotifyHandler:
    def __init__(self):
        self.__device_id = None
        self.__spotify = None
        self.__scope = ''
        account_info = 'account.env'
        redirect_uri = 'http://127.0.0.1:6400'
        auth_manager = self.__create_auth_manager(account_info, self.__scope, redirect_uri)
        self.__spotify = sp.Spotify(auth_manager=auth_manager)

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
