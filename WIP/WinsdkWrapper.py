import asyncio
import io

# from https://stackoverflow.com/questions/65011660/how-can-i-get-the-title-of-the-currently-playing-media-in-windows-10-with-python

# WinRT is now winsdk
from winsdk.windows.media.control import \
    GlobalSystemMediaTransportControlsSessionManager as MediaManager

from winsdk.windows.storage.streams import \
    DataReader, Buffer, InputStreamOptions

isPlaying = None
album_art_data = None

async def get_media_info():
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
            print(current_session.get_playback_info().playback_status == 4)

            return info_dict

    # It could be possible to select a program from a list of current
    # available ones. I just haven't implemented this here for my use case.
    # See references for more information.
    raise Exception('TARGET_PROGRAM is not the current media session')  

async def read_stream_into_buffer(stream_ref, buffer):
    readable_stream = await stream_ref.open_read_async()
    buffer = io.BytesIO()
    
    readable_stream.read_async(buffer, 50000000000, InputStreamOptions.READ_AHEAD)
    
    buffer.seek(0)  # Reset the buffer's position to the beginning
    return buffer


    


if __name__ == '__main__':
    current_media_info = asyncio.run(get_media_info())
    print(current_media_info)
    # create the current_media_info dict with the earlier code first
    thumb_stream_ref = current_media_info['thumbnail']
    print(dir(current_media_info['thumbnail']))

    # 5MB (5 million byte) buffer - thumbnail unlikely to be larger
    thumb_read_buffer = Buffer(5000000)
    print()

    # copies data from data stream reference into buffer created above
    bytes = asyncio.run(read_stream_into_buffer(thumb_stream_ref, thumb_read_buffer))

    with open('media_thumb.jpg', 'wb+') as fobj:
        fobj.write(bytearray(bytes))

    