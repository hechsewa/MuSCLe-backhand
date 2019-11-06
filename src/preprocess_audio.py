from pydub import effects, AudioSegment
import os

class Preprocessor:
    def __init__(self, v_path, v_dir):
        self.path = v_path
        self.dir = v_dir
        self.out_path = self.path.replace("mp3", "wav")

    def normalize(self):
        sound = AudioSegment.from_mp3(self.path)
        change_in_dBFS = -20.0 - sound.dBFS
        sound.apply_gain(change_in_dBFS)
        sound.set_frame_rate(44100)
        sound = effects.normalize(sound)
        self.out_path = self.out_path.replace("songs", "wavs")
        sound.export(self.out_path, format="wav", bitrate="16k")

    def rename_song(self, song_id):
        os.rename(r''+self.path, r''+self.dir+'/song'+str(song_id)+'.mp3')


def main():
    dir = '../../temp/player'
    song_id = -1
    for filename in os.listdir(dir):
        if filename.endswith(".mp3"):
            song_id += 1
            norma = Preprocessor(dir+"/"+filename, dir)
            norma.rename_song(song_id)


if __name__ == '__main__':
    main()