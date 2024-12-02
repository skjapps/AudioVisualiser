import requests
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import shutil
import os
import asyncio
import colorsys

from dotenv import load_dotenv
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
        self.results = None
        self.avg_colour_album_art = [255,255,255]
        self.vibrant_colour_album_art = [255,255,255]
        self.album_art_data = None
        self.artist_image_data = None
        self.cache_limit = cache_limit
        self.media_update_rate = media_update_rate

        # Storing media info, for any mode
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
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=self._scope,
                                                    client_id=os.getenv("SPOTIPY_CLIENT_ID"), 
                                                    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
                                                    redirect_uri="http://localhost:8080"))
            
        # private, setup
        self._sp_last_update = current_tick

        # Make cache folders
        if not os.path.exists('cache/'):
            os.makedirs('cache/')
            os.makedirs('cache/img')

        # First time get data
        asyncio.run(self.get_data())
    
    # Returns true for update, otherwise no update, i.e: skip album art
    async def update(self, current_tick):
        now = current_tick
        # 5000 ms = 5 seconds
        # Reduce api calls for now (IMPROVE WITH INTELLIGENT 429 error)
        if now - self._sp_last_update > (1000 * self.media_update_rate):
            # Reset timer
            self._sp_last_update = now
            await self.get_data()
            self.updated = True
        else:
            self.updated = False

    # if self.results are none, the data failed.
    async def get_data(self):
        try:
            if self.mode == "Spotify" :
                self.results = await asyncio.to_thread(self.sp.currently_playing)
                # print(self.results)
                # print(self.sp.current_user_recently_played(limit=1), "\n\n\n")
                if (self.song_name != self.results['item']['name']) or (self.artist_name != self.results['item']['artists'][0]['name']):
                    self.changed = True
                    # Set media related info
                    self.song_name = self.results['item']['name']
                    self.artist_name = self.results['item']['artists'][0]['name']
                    # print(self.results['is_playing'])
                    self.isPlaying = self.results['is_playing']
                    # Cache Album Art
                    self.album_art_data = await self.cache_image(self.results['item']['album']['images'][0]['url'], True)
                    artist_info = await asyncio.to_thread(self.sp.artist, self.results['item']['artists'][0]['uri'])
                    self.artist_image_data = await self.cache_image(artist_info['images'][0]['url'], False)
                    # print(self.sp.current_user_recently_played(limit=1), "\n\n\n")
                else:
                    self.changed = False
            # elif self.mode == "winsdk" :
            #     # Not caching windows album art data, no need.
            #     self.results = asyncio.run(self.get_media_info())
            #     self.song_name = self.results['title']
            #     self.artist_name = self.results['artist']
            #     print(self.artist_name)
            #     print(self.song_name)
            #     asyncio.run(self.get_album_art_win())
            #     self.get_avg_img_colour(self.album_art_data)
        except Exception as e:
            print(f"Error fetching data: {e}")
            self.results = None
            
        # self.results = None

    # Cache Album Art
    # Also saves the average colour of the current album art to "Colour"
    # get_colour either true or false
    async def CacheImage(self, url, get_colour):
        # Clear Cache above certain size
        if (self.get_folder_size('cache/') >= (self.cache_limit * 2 ** 20)):
            # Remove the folder and its contents
            shutil.rmtree('cache/')
            
            # Make the folders
            if not os.path.exists('cache/'):
                os.makedirs('cache/')
                os.makedirs('cache/img')

        # Find the url
        filename = 'cache/img/' + url.split('/')[-1] + '.jpg'
        
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
    
    # def get_canvas_token(self):
    #     CANVAS_TOKEN_URL = 'https://open.spotify.com/get_access_token?reason=transport&productType=web_player'
    #     response = requests.get(CANVAS_TOKEN_URL)
    #     if response.status_code == 200:
    #         return response.json()['accessToken']
    #     else:
    #         print(f"Error getting canvas token: {response.status_code} {response.text}")
    #         return None

    # def _get_personal_token(client_id, client_secret, refresh_token):
    #     PERSONAL_TOKEN_URL = 'https://accounts.spotify.com/api/token'
    #     auth_str = f"{client_id}:{client_secret}"
    #     b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    #     headers = {
    #         'Authorization': f'Basic {b64_auth_str}',
    #         'Content-Type': 'application/x-www-form-urlencoded'
    #     }
    #     data = {
    #         'grant_type': 'refresh_token',
    #         'refresh_token': refresh_token
    #     }
    #     response = requests.post(PERSONAL_TOKEN_URL, headers=headers, data=data)
    #     if response.status_code == 200:
    #         return response.json()['access_token']
    #     else:
    #         print(f"Error getting personal token: {response.status_code} {response.text}")
    #         return None

    # def get_canvases(self, song_id, canvas_token):
    #     CANVAS_API_URL = 'https://api.spotify.com/v1/tracks'
    #     headers = {
    #         'Authorization': f'Bearer {canvas_token}'
    #     }
    #     canvas = None
    #     track_id = track['track']['id']
    #     response = requests.get(f"{CANVAS_API_URL}/{track_id}", headers=headers)
    #     if response.status_code == 200:
    #         track_info = response.json()
    #         canvas_url = track_info.get('album', {}).get('images', [{}]).get('url')
    #         if canvas_url and canvas_url.endswith('.mp4'):
    #             canvas = ({
    #                 'uri': track['track']['uri'],
    #                 'name': track['track']['name'],
    #                 'previewUrl': track['track']['preview_url'],
    #                 'canvasUrl': canvas_url
    #             })
    #     else:
    #         print(f"Error getting canvas for track {track_id}: {response.status_code} {response.text}")
    #     return canvas