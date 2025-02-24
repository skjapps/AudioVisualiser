import requests
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheFileHandler
import shutil
import os
import colorsys
import asyncio
import threading

from dotenv import load_dotenv
from PIL import Image
from pathlib import Path

from Default import Functions

# WinRT is now winsdk
import winsdk.windows.media.control as wmc # for media info
import winsdk.windows.storage.streams as streams # For data stream


def list_active_threads():
    threads = threading.enumerate()
    print(f"Active threads ({len(threads)}):")
    for thread in threads:
        print(f"- {thread.name}")

#####################################
#           SPOTIPY/Winsdk          #
#####################################
class MediaInfoWrapper():
    
    def __init__(self, mode, current_tick, cache_limit, media_update_rate):
        # Setup
        self.mode = mode
        self.results = None
        self.avg_colour_album_art = [255,255,255]
        self.vibrant_colour_album_art = [255,255,255]
        self.album_art_data = None
        self.artist_image_data = None
        self.cache_limit = cache_limit
        self.media_update_rate = media_update_rate

        # Storing media info, for any mode
        self.item = None
        self.song_name = None
        self.artist_name = None
        self.isPlaying = False
        self.updated = False # When data is updated, this is True (avoid thread blocking)
        self.changed = False
        self.new_data = False # If data is new, this is True (i.e: to indicate change in song)

        # spotify related
        self._scope = "user-read-currently-playing user-read-recently-played" # Only need what user is listening to. 
        load_dotenv()
        # The spotify api object
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                                        scope=self._scope,
                                        # client_id=os.getenv("SPOTIPY_CLIENT_ID"), 
                                        # client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
                                        client_id="f4b901c18dcf4bd98dc8e7624804d7f6", 
                                        client_secret="bae6111d2ddf40f597c8dfb82c495227",
                                        redirect_uri="http://localhost:8080",
                                        cache_handler=CacheFileHandler(
                                            cache_path=Functions.resource_path('.cache'))))
        
        # private, setup
        self._sp_last_update = current_tick

        # Make cache folders
        if not os.path.exists(Functions.resource_path('cache/')):
            os.makedirs(Functions.resource_path('cache/'))
            os.makedirs(Functions.resource_path('cache/img/'))
    
    # Returns true for update, otherwise no update, i.e: skip album art
    async def update(self, current_tick):
        now = current_tick
        # 5000 ms = 5 seconds
        # Reduce api calls for now (IMPROVE WITH INTELLIGENT 429 error)
        if now - self._sp_last_update > (1000 * self.media_update_rate):
            # Reset timer
            self._sp_last_update = now
            # Get data
            await self.get_data()

            # print("Updated spotify data \n")
            
            self.updated = True
        else:
            self.updated = False

    # if self.results are none, the data failed.
    async def get_data(self):
        try:
            if self.mode == "Spotify" :
                # print("Calling Spotify (2x)")
                self.results = self.sp.currently_playing()
                # print(self.results)
                if (self.results['item'] != self.item):
                    self.changed = True
                else:
                    self.changed = False
                # Set media related info
                self.item = self.results['item'] # The item holds a lot of unique data
                self.song_name = self.results['item']['name']
                self.artist_name = ""
                for artist in self.results['item']['artists'] : self.artist_name += (str(artist['name']) + ", ")
                self.artist_name = self.artist_name[:-2]
                # print(self.results['is_playing'])
                self.isPlaying = self.results['is_playing']
                # Cache Album Art
                self.album_art_data = self.CacheImage(self.results['item']['album']['images'][0]['url'], True)
                artist_info = self.sp.artist(self.results['item']['artists'][0]['uri'])
                # print(artist_info)
                self.artist_image_data = self.CacheImage(artist_info['images'][0]['url'], False)
                # print(self.sp.current_user_recently_played(limit=1), "\n\n\n")
            elif self.mode == "winsdk" :
                # Not caching windows album art data, no need.
                self.song_name, self.artist_name, self.album_art_data = await self.get_media_info()
                self.artist_image_data = self.album_art_data # both are album art, as theres no artist image - to improve
                self.get_avg_img_colour(self.album_art_data)
        except:
            # Return Default Values...
            # print("return default values \n")
            self.song_name = "Loading..."
            self.artist_name = "Play Spotify Music..."
            self.album_art_data = self.artist_image_data = open(Functions.resource_path('assets/ico/ico.png'), 'rb').read()
            self.results = None

    # getting data with WinSDK
    async def get_media_info(self):
        sessions = await wmc.GlobalSystemMediaTransportControlsSessionManager.request_async()
        current_session = sessions.get_current_session()
        if current_session:
            info = await current_session.try_get_media_properties_async()
            # dir(info) = 'album_artist', 'album_title', 'album_track_count', 'artist', 'genres', 'playback_type', 'subtitle', 'thumbnail', 'title', 'track_number'

            # Get album art as a RandomAccessStreamReference
            thumbnail = info.thumbnail
            if thumbnail:
                list_active_threads()
                stream = await thumbnail.open_read_async()
                size = stream.size
                buffer = streams.Buffer(size)
                await stream.read_async(buffer, size, streams.InputStreamOptions.NONE)
                
                # Use DataReader to read bytes from the buffer
                data_reader = streams.DataReader.from_buffer(buffer)
                byte_array = bytearray(size)
                data_reader.read_bytes(byte_array)
                # return the byte_array as media info

                # image = Image.open(BytesIO(byte_array))
                # image.show()

            # in order: song_name, artist_name, album_art_data
            return info.title, info.artist, byte_array
            
    # Cache Album Art
    # Also saves the average colour of the current album art to "Colour"
    # get_colour either true or false
    def CacheImage(self, url, get_colour):
        try:
            # Clear Cache above certain size
            if (self.get_folder_size(Functions.resource_path('cache/')) >= (self.cache_limit * 2 ** 20)):
                # Remove the folder and its contents
                shutil.rmtree(Functions.resource_path('cache/'))
                
                # Make the folders
                if not os.path.exists(Functions.resource_path('cache/')):
                    os.makedirs(Functions.resource_path('cache/'))
                    os.makedirs(Functions.resource_path('cache/img'))

            # Find the url
            filename = Functions.resource_path('cache/img/' + url.split('/')[-1] + '.jpg')
            
            # Load image data and save if needed
            try:
                ret = open(filename, 'rb').read()
            except FileNotFoundError:
                ret = requests.get(url).content
                with open(filename, 'wb') as handler:
                    handler.write(ret)

            # Average image colour 
            if get_colour:
                # self.get_vibrant_img_colour(filename)
                self.get_avg_img_colour(filename)

            return ret
        except Exception as e:
            print(e)

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

    def get_vibrant_img_colour(self, filename):
        # Load the image
        image = Image.open(filename)
        # Convert the image to a NumPy array
        image_array = np.array(image)
        
        # Normalize the RGB values to the range [0, 1]
        image_array = image_array / 255.0
        
        # Convert RGB to HSV
        hsv_image = np.zeros_like(image_array)
        hsv_image[..., 0], hsv_image[..., 1], hsv_image[..., 2] = np.vectorize(colorsys.rgb_to_hsv)(
            image_array[..., 0], image_array[..., 1], image_array[..., 2]
        )
        
        # Find the index of the pixel with the highest saturation and value
        max_saturation_value_index = np.argmax(hsv_image[..., 1] * hsv_image[..., 2])
        
        # Convert the index back to 2D coordinates
        max_saturation_value_coords = np.unravel_index(max_saturation_value_index, hsv_image[..., 1].shape)
        
        # Get the RGB value of the most vibrant color
        vibrant_color = image_array[max_saturation_value_coords]
        
        # Convert back to the range [0, 255]
        self.vibrant_colour_album_art = (vibrant_color * 255).astype(int).tolist()
        
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