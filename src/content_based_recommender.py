import numpy as np
import pandas as pd


class ContentBasedRecommender:
    def __init__(self, all_grades, user_id, path):
        self.user_grades = [(s[1], s[2]) for s in all_grades if s[0] == user_id]
        self.user_songs = [s[0] for s in self.user_grades]
        self.data = self.read_csv(path)
        self.user_profile = self.get_user_profile()
        self.recommended = self.get_recommendation()

    def get_user_profile(self):
        feature_matrix = self.data.loc[self.data['nr'].isin(self.user_songs)]
        user_grades = [s[1] for s in self.user_grades]
        m = np.delete(np.array(feature_matrix), 0, 1)
        c = np.array(user_grades)
        weighted_matrix = m * c[:, np.newaxis]
        user_profile = np.sum(weighted_matrix, 0)
        user_profile_norm = user_profile/np.sum(user_profile)
        return user_profile_norm

    def get_recommendation(self):
        black_box = self.data.loc[~self.data['nr'].isin(self.user_songs)]
        m = np.delete(np.array(black_box), 0, 1)
        weighted_rec = np.sum(m, 1)
        amax = np.amax(weighted_rec)
        #sort reverse and get first 10 items
        sorted_arr = np.sort(weighted_rec)
        sorted_rev = sorted_arr[::-1]
        rec = sorted_rev[1:108]
        indexes = []
        for item in rec:
            ind = np.where(weighted_rec == item)[0][0]
            indexes.append(ind)
        rec_std = np.divide(rec-rec.mean(), rec.max()-rec.min())
        data = {'song_id': indexes, 'rec': rec_std}
        df = pd.DataFrame(data)
        return df

    def read_csv(self, path):
        df = pd.read_csv(path)
        df = df[['nr', 'bpm', 'spec flat', 'spec skew', 'kurt', 'zero cross', 'hpss', 'vocal']]
        return df


def main():
    cb = ContentBasedRecommender([[1,4,3],[1,2,4],[2,3,2], [1,3,2]], 1, './data.csv')
    print(cb.recommended)


if __name__ == '__main__':
    main()