import os
import eyed3
import stagger
import io

# Pobiera odpowiednie metadata z plikow audio
from flask_sqlalchemy import SQLAlchemy

from backhand import models
from backhand.__init__ import db

class Metadata:
    def __init__(self, v_path):
        self.path = v_path
        self.loaded = eyed3.load(self.path)

    def get_artist(self):
        return self.loaded.tag.artist

    def get_album(self):
        return self.loaded.tag.album

    def get_title(self):
        return self.loaded.tag.title

    def get_genre(self):
        if str(self.loaded.tag.genre) != '':
            return str(self.loaded.tag.genre)
        else:
            return None

    def get_cover(self):
        try:
            audio_tag = stagger.read_tag(self.path)
            byte_im = audio_tag[stagger.id3.PIC][0].data
            im = io.BytesIO(byte_im).getvalue()
            return im
        except KeyError:
            return None

def main():
    nr = -1

    dir_src = '../../temp/songs'
    for filename in os.listdir(dir_src):
        if filename.endswith(".mp3"):
            nr += 1
            filepath = "../../temp/player/song"+str(nr)+".mp3"
            serverpath = "http://muscle-client.herokuapp.com/song/songs/song"+str(nr)+".mp3"

            metadata = Metadata(filepath)
            artist = metadata.get_artist()
            album = metadata.get_album()
            title = metadata.get_title()
            genre = metadata.get_genre()
            cover = metadata.get_cover()
            print("song"+str(nr)+": "+str(cover))
            # save to db
            song = models.Song(src=serverpath, img=cover)
            meta = models.Metadata(title=title, band=artist, genre=genre, album=album)
            db.session.add(song)
            db.session.add(meta)

    db.session.commit()


if __name__ == '__main__':
    main()
