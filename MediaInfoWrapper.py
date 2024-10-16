import requests
import numpy as np
import io
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import shutil
import os
import threading
import asyncio

from PIL import Image

# WinRT is now winsdk
from winsdk.windows.media.control import \
    GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winsdk.windows.storage.streams import \
    DataReader, Buffer, InputStreamOptions

#####################################
#           SPOTIPY/Winsdk          #
#####################################
class MediaInfoWrapper():
    def __init__(self, mode, current_tick, cache_limit, media_update_rate):
        # Setup
        self.mode = mode
        self.avg_colour_album_art = [255,255,255]
        self.album_art_data = None
        self.cache_limit = cache_limit
        self.media_update_rate = media_update_rate

        # Storing media info, for any mode
        self.song_name = None
        self.artist_name = None
        self.isPlaying = False
        self.updated = False # When data is updated, this is True (avoid thread blocking)

        # spotify related
        self._scope = "user-read-currently-playing" # Only need what user is listening to. 
        # The spotify api object
        if mode == "Spotify" :
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=self._scope, 
                                                        client_id="f4b901c18dcf4bd98dc8e7624804d7f6", 
                                                        client_secret="1c2d3272146545f7a25d0657884c65fe",
                                                        redirect_uri="http://localhost:8080"))
            
        # private, setup
        self._sp_last_update = current_tick
        self._lock = threading.Lock()

        # Make cache folders
        if not os.path.exists('cache/'):
            os.makedirs('cache/')
            os.makedirs('cache/img')

        # First time get data
        self.get_data()
    
    # Returns true for update, otherwise no update, i.e: skip album art
    def update(self, current_tick):
        now = current_tick
        # 5000 ms = 5 seconds
        # Reduce api calls for now (IMPROVE WITH INTELLIGENT 429 error)
        if now - self._sp_last_update > (1000 * self.media_update_rate):
            # Reset timer
            self._sp_last_update = now

            # Start a new thread to get data
            threading.Thread(target=self.get_data).start()

    # if self.results are none, the data failed.
    def get_data(self):
        try:
            if self.mode == "Spotify" :
                self.results = self.sp.currently_playing()
                # Set media related info
                self.song_name = self.results['item']['name']
                self.artist_name = self.results['item']['artists'][0]['name']
                # self.isPlaying = eval(self.results['is_playing'])
                print(eval(self.results['is_playing']))
                # Cache Album Art
                self.CacheAlbumArt()
                # print(self.results)
            # elif self.mode == "winsdk" :
            #     # Not caching windows album art data, no need.
            #     self.results = asyncio.run(self.get_media_info())
            #     self.song_name = self.results['title']
            #     self.artist_name = self.results['artist']
            #     print(self.artist_name)
            #     print(self.song_name)
            #     asyncio.run(self.get_album_art_win())
            #     self.get_avg_img_colour(self.album_art_data)
        except:
            self.results = None

        self.updated = True
        # self.results = None              

    async def get_media_info(self):
        sessions = await MediaManager.request_async()

        # This source_app_user_model_id check and if statement is optional
        # Use it if you want to only get a certain player/program's media
        # (e.g. only chrome.exe's media not any other program's).

        # To get the ID, use a breakpoint() to run sessions.get_current_session()
        # while the media you want to get is playing.
        # Then set TARGET_ID to the string this call returns.

        current_session = sessions.get_current_session()
        if current_session:  # there needs to be a media session running
            # print(current_session.source_app_user_model_id)
            if current_session.source_app_user_model_id == current_session.source_app_user_model_id:

                info = await current_session.try_get_media_properties_async()

                # song_attr[0] != '_' ignores system attributes
                info_dict = {song_attr: info.__getattribute__(song_attr) for song_attr in dir(info) if song_attr[0] != '_'}

                # converts winrt vector to list
                info_dict['genres'] = list(info_dict['genres'])

                # Current Playing status (4 is Playing and 5 is Not)
                self.isPlaying = current_session.get_playback_info().playback_status == 4

                return info_dict

        # It could be possible to select a program from a list of current
        # available ones. I just haven't implemented this here for my use case.
        # See references for more information.
        raise Exception('TARGET_PROGRAM is not the current media session')  
    
    async def get_album_art_win(self):
        # create the current_media_info dict with the earlier code first
        thumb_stream_ref = self.results['thumbnail']

        # 5MB (5 million byte) buffer - thumbnail unlikely to be larger
        thumb_read_buffer = Buffer(5000000)

        # copies data from data stream reference into buffer created above
        await self.read_stream_into_buffer(thumb_stream_ref, thumb_read_buffer)

        # reads data (as bytes) from buffer
        buffer_reader = DataReader.from_buffer(thumb_read_buffer)
        self.album_art_data = buffer_reader.read_bytes(thumb_read_buffer.length)
        print("Got album art")

    async def read_stream_into_buffer(self, stream_ref, buffer):
        readable_stream = await stream_ref.open_read_async()
        await readable_stream.read_async(buffer, buffer.capacity, InputStreamOptions.READ_AHEAD)


    # Cache Album Art
    # Also saves the average colour of the current album art to "Colour"
    def CacheAlbumArt(self):
        # Clear Cache above certain size
        if (self.get_folder_size('cache/') >= (self.cache_limit * 2 ** 20)):
            # Remove the folder and its contents
            shutil.rmtree('cache/')
            
            # Make the folders
            if not os.path.exists('cache/'):
                os.makedirs('cache/')
                os.makedirs('cache/img')

        # Find the url
        url = self.results['item']['album']['images'][0]['url']
        filename = 'cache/img/' + url.split('/')[-1] + '.jpg'
        
        # Load image data and save if needed
        try:
            self.album_art_data = open(filename, 'rb').read()
        except FileNotFoundError:
            self.album_art_data = requests.get(self.results['item']['album']['images'][0]['url']).content
            with open(filename, 'wb') as handler:
                handler.write(self.album_art_data)

        self.get_avg_img_colour(filename)

    def get_avg_img_colour(self, filename):
        # Average image colour 
        # Load the image
        image = Image.open(filename)
        # Convert the image to a NumPy array
        image_array = np.array(image)
        # Calculate the average RGB values
        self.avg_colour_album_art = np.mean(image_array, axis=(0, 1))

        # Check if the result is a single number (greyscale or single channel...)
        if np.isscalar(self.avg_colour_album_art):
            self.avg_colour_album_art = np.array([self.avg_colour_album_art] * 3)
        

    # From https://stackoverflow.com/questions/1392413/calculating-a-directorys-size-using-python
    def get_folder_size(self, start_path = '.'):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)

        return total_size