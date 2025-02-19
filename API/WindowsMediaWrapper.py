import asyncio
from PIL import Image
from io import BytesIO

# WinRT is now winsdk
import winsdk.windows.media.control as wmc # for media info
import winsdk.windows.storage.streams as streams # For data stream


#####################################
#           SPOTIPY/Winsdk          #
#####################################
class WindowsMediaWrapper():
    def __init__(self):
        # Setup
        self.results = None
        
        # first time run...
        print(asyncio.run(self.get_media_info()))

    async def get_media_info(self):
        sessions = await wmc.GlobalSystemMediaTransportControlsSessionManager.request_async()
        current_session = sessions.get_current_session()
        if current_session:
            info = await current_session.try_get_media_properties_async()
            # dir info = 'album_artist', 'album_title', 'album_track_count', 'artist', 'genres', 'playback_type', 'subtitle', 'thumbnail', 'title', 'track_number'

            # Get album art as a RandomAccessStreamReference
            thumbnail = info.thumbnail
            if thumbnail:
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

wmr = WindowsMediaWrapper()
asyncio.run(wmr.get_media_info())