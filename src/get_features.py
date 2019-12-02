import csv
import librosa  # https://librosa.github.io/
import math     # do zaokraglania wartosci
import numpy
import pandas as pd
import sklearn
from pydub import AudioSegment  # konwersja do wav
import scipy
from scipy import signal
import os


def normalize(csv_data):
    csv_end = ['bpm', 'spec flat', 'spec skew', 'kurt', 'zero cross', 'hpss', 'vocal',
                 'bin1', 'bin2', 'bin3', 'bin4', 'bin5', 'bin6',
                 'bin1 mean freq', 'bin1 std', 'bin1 q25', 'bin1 q75',
                 'bin2 mean freq', 'bin2 std', 'bin2 q25', 'bin2 q75',
                 'bin3 mean freq', 'bin3 std', 'bin3 q25', 'bin3 q75',
                 'bin4 mean freq', 'bin4 std', 'bin4 q25', 'bin4 q75',
                 'bin5 mean freq', 'bin5 std', 'bin5 q25', 'bin5 q75',
                 'bin6 mean freq', 'bin6 std', 'bin6 q25', 'bin6 q75']
    csv_end_2 = [['bpm', 'spec flat', 'spec skew', 'kurt', 'zero cross', 'hpss', 'vocal',
                 'bin1', 'bin2', 'bin3', 'bin4', 'bin5', 'bin6',
                 'bin1 mean freq', 'bin1 std', 'bin1 q25', 'bin1 q75',
                 'bin2 mean freq', 'bin2 std', 'bin2 q25', 'bin2 q75',
                 'bin3 mean freq', 'bin3 std', 'bin3 q25', 'bin3 q75',
                 'bin4 mean freq', 'bin4 std', 'bin4 q25', 'bin4 q75',
                 'bin5 mean freq', 'bin5 std', 'bin5 q25', 'bin5 q75',
                 'bin6 mean freq', 'bin6 std', 'bin6 q25', 'bin6 q75', 'nr']]
    normal = sklearn.preprocessing.normalize(csv_data, norm='l2', axis=1, copy=True, return_norm=False)
    df = pd.DataFrame(normal, columns=csv_end)
    df['nr'] = numpy.arange(108)
    csv_end = numpy.concatenate((csv_end_2, df.values))
    return csv_end


class FeatureSet:
    def __init__(self, v_path):
        self.path = v_path
        self.wave, self.sample_rate = librosa.load(self.path)
        self.stft = numpy.abs(librosa.core.stft(self.wave))
        self.vocal = self.get_vocal()
        self.hist = self.split_into_bins()

    def convert_to_wav(self):
        sound = AudioSegment.from_mp3(self.path)
        dst = '../temp/test.wav'  # sciezka do pliku temp wav
        sound.export(dst, format="wav")
        return dst

    def get_bpm(self):
        tempo = librosa.beat.tempo(self.wave)
        tempo = math.floor(tempo)
        return tempo

    # mean frequency (kHz) for a bin of frequencies
    def get_mean_freq(self, bin_freq):
        # bin_freq = numpy.nanmean(bin_freq)
        mean = numpy.mean(bin_freq)
        if math.isnan(mean):
            mean = 0
        return mean

    # standard derivation bin of frequencies
    def get_standard_dev(self, bin_freq):
        # bin_freq = numpy.nanmean(bin_freq)
        sd = numpy.sqrt(numpy.mean(abs(bin_freq - numpy.mean(bin_freq)) ** 2))
        if math.isnan(sd):
            sd = 0
        return sd

    # 1 kwantyl/mediana dla bin of frequencies
    def get_q25(self, bin_freq):
        # bin_freq = numpy.nanmean(bin_freq)
        try:
            q25 = numpy.quantile(bin_freq, 0.25)
        except IndexError:
            q25 = 0
        if math.isnan(q25):
            q25 = 0
        return q25

    # 3 kantyl dla bin of freq
    def get_q75(self, bin_freq):
        # bin_freq = numpy.nanmean(bin_freq)
        try:
            q75 = numpy.quantile(bin_freq, 0.75)
        except IndexError:
            q75 = 0
        if math.isnan(q75):
            q75 = 0
        return q75

    # how noise-like a sound is, as opposed to being tone-like (closer to 1 - white noise)
    def get_spectral_flatness(self):
        flatness = librosa.feature.spectral_flatness(y=self.wave)
        filtered = [x for x in flatness[0] if x > 0.02]  # check if signal is noisy
        no = len(filtered)
        return no

    # miara asymetryczności rozkładu w okolicach średniej wartości
    def get_spectral_skew(self):
        skew = scipy.stats.skew(abs(self.wave))
        if skew == 0:  # symetryczne
            return 0
        elif skew < 0:  # na prawo
            return 1
        else:  # skew>0, na lewo
            return 2

    def get_kurtosis(self):
        kurt = scipy.stats.kurtosis(self.wave)
        return kurt

    def get_zero_crossings(self):
        zero_crossings = librosa.zero_crossings(self.wave, pad=False)
        return sum(zero_crossings)

    # znajdz najwiekszy srodek masy audio
    def get_spectral_centroid(self):
        spectral_centroids = librosa.feature.spectral_centroid(self.wave, self.sample_rate)[0]
        return spectral_centroids

    # wyznacz Mel-frequency cepstral coefficients (MFCCs)
    def get_mfccs(self):
        mfccs = librosa.feature.mfcc(self.wave)
        return mfccs

    # Harmonic-percussive source separation
    def get_hpss(self):
        D = librosa.stft(self.wave)
        D_harmonic, D_percussive = librosa.decompose.hpss(D)
        D_harmonic = numpy.mean(abs(D_harmonic))
        D_percussive = numpy.mean(abs(D_percussive))
        if D_harmonic > D_percussive:
            return 1  # 'harmonic'
        else:
            return 0  # 'percussive'

    # If track has vocal or not
    def get_vocal(self):
        # And compute the spectrogram magnitude and phase
        S_full, phase = librosa.magphase(librosa.stft(self.wave))
        S_filter = librosa.decompose.nn_filter(S_full,
                                               aggregate=numpy.median,
                                               metric='cosine',
                                               width=int(librosa.time_to_frames(2, sr=self.sample_rate)))
        S_filter = numpy.minimum(S_full, S_filter)
        margin_i, margin_v = 2, 10
        power = 2

        mask_i = librosa.util.softmask(S_filter,
                                       margin_i * (S_full - S_filter),
                                       power=power)

        mask_v = librosa.util.softmask(S_full - S_filter,
                                       margin_v * S_filter,
                                       power=power)
        S_foreground = mask_v * S_full
        comps, acts = librosa.decompose.decompose(S_foreground, n_components=16, sort=True)  # decomposition
        if numpy.count_nonzero(comps) < 10000:
            return 0  # no vocal
        else:
            return 1  # vocal

    def split_into_bins(self):
        _, _, spectrogram = signal.spectrogram(self.wave, self.sample_rate)
        bin_size = numpy.max(spectrogram)/6
        hist, _ = numpy.histogram(spectrogram,
                                  bins=[0, bin_size, 2*bin_size, 3*bin_size, 4*bin_size, 5*bin_size, 6*bin_size])
        return hist

    def get_bin_no(self, no):
        _, _, spectrogram = signal.spectrogram(self.wave, self.sample_rate)
        bin_size = numpy.max(spectrogram)/6
        spectrogram = spectrogram.flatten()
        bin_scale = [x for x in spectrogram if (x>((no-1)*bin_size) and x<=((no)*bin_size))]
        #print(bin_scale)
        return bin_scale


def main():

    # make a csv file and header
    csv_data = [['nr', 'bpm', 'spec flat', 'spec skew', 'kurt', 'zero cross', 'hpss', 'vocal',
                'bin1', 'bin2', 'bin3', 'bin4', 'bin5', 'bin6',
                'bin1 mean freq', 'bin1 std', 'bin1 q25', 'bin1 q75',
                'bin2 mean freq', 'bin2 std', 'bin2 q25', 'bin2 q75',
                'bin3 mean freq', 'bin3 std', 'bin3 q25', 'bin3 q75',
                'bin4 mean freq', 'bin4 std', 'bin4 q25', 'bin4 q75',
                'bin5 mean freq', 'bin5 std', 'bin5 q25', 'bin5 q75',
                'bin6 mean freq', 'bin6 std', 'bin6 q25', 'bin6 q75']]

    nr = -1

    dir_src = '../../temp/wavs'
    for filename in os.listdir(dir_src):
        if filename.endswith(".wav"):
            nr += 1
            features = FeatureSet(dir_src+"/"+filename)
            # whole track features
            bpm = str(features.get_bpm())
            spec_flat = str(features.get_spectral_flatness())
            spec_skew = str(features.get_spectral_skew())
            kurt = str(features.get_kurtosis())
            zero_cross = str(features.get_zero_crossings())
            hpss = str(features.get_hpss())
            vocal = str(features.get_vocal())

            # bins stats
            bins = features.split_into_bins()
            bin_count_1 = str(bins[0])
            bin_count_2 = str(bins[1])
            bin_count_3 = str(bins[2])
            bin_count_4 = str(bins[3])
            bin_count_5 = str(bins[4])
            bin_count_6 = str(bins[5])

            # bins 1 features
            bin1 = features.get_bin_no(0)
            bin_mf_1 = str(features.get_mean_freq(bin1))
            bin_std_1 = str(features.get_standard_dev(bin1))
            bin_q25_1 = str(features.get_q25(bin1))
            bin_q75_1 = str(features.get_q75(bin1))

            # bins 2 features
            bin2 = features.get_bin_no(1)
            bin_mf_2 = str(features.get_mean_freq(bin2))
            bin_std_2 = str(features.get_standard_dev(bin2))
            bin_q25_2 = str(features.get_q25(bin2))
            bin_q75_2 = str(features.get_q75(bin2))

            # bins 3 features
            bin3 = features.get_bin_no(2)
            bin_mf_3 = str(features.get_mean_freq(bin3))
            bin_std_3 = str(features.get_standard_dev(bin3))
            bin_q25_3 = str(features.get_q25(bin3))
            bin_q75_3 = str(features.get_q75(bin3))

            # bins 4 features
            bin4 = features.get_bin_no(3)
            bin_mf_4 = str(features.get_mean_freq(bin4))
            bin_std_4 = str(features.get_standard_dev(bin4))
            bin_q25_4 = str(features.get_q25(bin4))
            bin_q75_4 = str(features.get_q75(bin4))

            # bins 5 features
            bin5 = features.get_bin_no(4)
            bin_mf_5 = str(features.get_mean_freq(bin5))
            bin_std_5 = str(features.get_standard_dev(bin5))
            bin_q25_5 = str(features.get_q25(bin5))
            bin_q75_5 = str(features.get_q75(bin5))

            # bins 6 features
            bin6 = features.get_bin_no(5)
            bin_mf_6 = str(features.get_mean_freq(bin6))
            bin_std_6 = str(features.get_standard_dev(bin6))
            bin_q25_6 = str(features.get_q25(bin6))
            bin_q75_6 = str(features.get_q75(bin6))

            # save row to csv
            row = [nr, bpm, spec_flat, spec_skew, kurt, zero_cross, hpss, vocal,
                   bin_count_1, bin_count_2, bin_count_3, bin_count_4, bin_count_5, bin_count_6,
                   bin_mf_1, bin_std_1, bin_q25_1, bin_q75_1,
                   bin_mf_2, bin_std_2, bin_q25_2, bin_q75_2,
                   bin_mf_3, bin_std_3, bin_q25_3, bin_q75_3,
                   bin_mf_4, bin_std_4, bin_q25_4, bin_q75_4,
                   bin_mf_5, bin_std_5, bin_q25_5, bin_q75_5,
                   bin_mf_6, bin_std_6, bin_q25_6, bin_q75_6]
            csv_data.append(row)

    with open('data.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(csv_data)
    csv_file.close()


def main_norm():
    df = pd.read_csv("data.csv")
    norm = normalize(df.iloc[:, 1:].values)
    with open('data_norm.csv', 'w') as csv_file:
        wr = csv.writer(csv_file)
        wr.writerows(norm)
    csv_file.close()


if __name__ == '__main__':
    main_norm()


