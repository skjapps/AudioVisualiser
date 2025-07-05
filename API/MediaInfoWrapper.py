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

from Default import functions

def list_active_threads():
    threads = threading.enumerate()
    print(f"Active threads ({len(threads)}):")
    for thread in threads:
        print(f"- {thread.name}")

#####################################
#           SPOTIPY ONLY           #
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
                                            cache_path=functions.resource_path('.cache'))))
        
        # private, setup
        self._sp_last_update = current_tick

        # Make cache folders
        if not os.path.exists(functions.resource_path('cache/')):
            os.makedirs(functions.resource_path('cache/'))
            os.makedirs(functions.resource_path('cache/img/'))
    
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
                
                # Check if we got valid results and item
                if self.results is None or self.results.get('item') is None:
                    self.song_name = "No Song Playing"
                    self.artist_name = "Play Spotify Music..."
                    self.album_art_data = self.artist_image_data = open(functions.resource_path('assets/ico/ico.png'), 'rb').read()
                    self.results = None
                    return
                
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
                if self.results['item']['album']['images']:
                    self.album_art_data = self.CacheImage(self.results['item']['album']['images'][0]['url'], True)
                else:
                    self.album_art_data = open(functions.resource_path('assets/ico/ico.png'), 'rb').read()
                
                artist_info = self.sp.artist(self.results['item']['artists'][0]['uri'])
                # print(artist_info)
                if artist_info and artist_info.get('images'):
                    self.artist_image_data = self.CacheImage(artist_info['images'][0]['url'], False)
                else:
                    self.artist_image_data = open(functions.resource_path('assets/ico/ico.png'), 'rb').read()
                # print(self.sp.current_user_recently_played(limit=1), "\n\n\n")
            else:
                # For non-Spotify modes, return default values
                self.song_name = "No Media Info Available"
                self.artist_name = "Use Spotify Mode"
                self.album_art_data = self.artist_image_data = open(functions.resource_path('assets/ico/ico.png'), 'rb').read()
                self.results = None
        except:
            # Return Default Values...
            # print("return default values \n")
            self.song_name = "Loading..."
            self.artist_name = "Play Spotify Music..."
            self.album_art_data = self.artist_image_data = open(functions.resource_path('assets/ico/ico.png'), 'rb').read()
            self.results = None

    # Cache Album Art
    # Also saves the average colour of the current album art to "Colour"
    # get_colour either true or false
    def CacheImage(self, url, get_colour):
        try:
            # Clear Cache above certain size
            if (self.get_folder_size(functions.resource_path('cache/')) >= (self.cache_limit * 2 ** 20)):
                # Remove the folder and its contents
                shutil.rmtree(functions.resource_path('cache/'))
                
                # Make the folders
                if not os.path.exists(functions.resource_path('cache/')):
                    os.makedirs(functions.resource_path('cache/'))
                    os.makedirs(functions.resource_path('cache/img'))

            # Find the url
            filename = functions.resource_path('cache/img/' + url.split('/')[-1] + '.jpg')
            
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
        
        # Calculate the average color
        avg_color = np.mean(image_array, axis=(0, 1))
        
        # Convert to RGB values (0-255)
        self.avg_colour_album_art = [int(avg_color[0]), int(avg_color[1]), int(avg_color[2])]

    def get_vibrant_img_colour(self, filename):
        # Load the image
        image = Image.open(filename)
        # Convert the image to a NumPy array
        image_array = np.array(image)
        
        # Calculate the average color
        avg_color = np.mean(image_array, axis=(0, 1))
        
        # Convert to RGB values (0-255)
        self.vibrant_colour_album_art = [int(avg_color[0]), int(avg_color[1]), int(avg_color[2])]

    def get_folder_size(self, start_path = '.'):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)

        return total_size