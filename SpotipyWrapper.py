import requests
import numpy as np
import io
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import shutil
import os

from PIL import Image


#####################################
#              SPOTIPY              #
#####################################
class SpotipyWrapper():
    def __init__(self, current_tick, cache_limit):
        # Setup
        self.avg_colour_album_art = [255,255,255]
        self.album_art_data = None
        self.cache_limit = cache_limit
        self._scope = "user-read-currently-playing" # Only need what user is listening to. 
        # The spotify api object
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=self._scope, 
                                                    client_id="f4b901c18dcf4bd98dc8e7624804d7f6", 
                                                    client_secret="1c2d3272146545f7a25d0657884c65fe",
                                                    redirect_uri="http://localhost:8080"))
        self._sp_last_update = current_tick

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
        if now - self._sp_last_update > 5000:
            # Reset timer
            self._sp_last_update = now

            self.get_data()

            return True
        
        return False

    # if self.results are none, the data failed.
    def get_data(self):
        try:
            self.results = self.sp.currently_playing()
            # Cache Album Art
            self.CacheAlbumArt()
        except:
            self.results = None
        
        # self.results = None                


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