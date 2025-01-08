import os
import musicbrainzngs

class MusicbrainzWrapper():
    def __init__(self):
        musicbrainzngs.auth(os.getenv("MUSICBRAINZ_CLIENT_KEY"), 
                            os.getenv("MUSICBRAINZ_CLIENT_SECRET"))
        
        # Tell musicbrainz what your app is, and how to contact you
        # (this step is required, as per the webservice access rules
        # at http://wiki.musicbrainz.org/XML_Web_Service/Rate_Limiting )
        musicbrainzngs.set_useragent("AudioVisualiser", "0.8", 
                                    "http://www.github.com/skjapps/audiovisualiser")

    def get_artist_id_from_track(self, track_name, artist_name):
        result = musicbrainzngs.search_recordings(query=f"{track_name} AND artist:{artist_name}", limit=1)
        if result['recording-list']:
            return result['recording-list'][0]['artist-credit'][0]['artist']['id']
        return None
    
    def get_artist_cover_image(self, artist_id):
        try:
            cover_art = musicbrainzngs.get_image_
            return cover_art
        except musicbrainzngs.ResponseError as e:
            print(f"Error retrieving cover art: {e}")
            return None

    def get_images(self):
        print (musicbrainzngs.get_artist_by_id("952a4205-023d-4235-897c-6fdb6f58dfaa", []))

mbwrapper = MusicbrainzWrapper()
# print((mbwrapper.search_artist("WRLD")))
print(mbwrapper.get_artist_cover_image(mbwrapper.get_artist_id_from_track("By Design", "WRLD")))