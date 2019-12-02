import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler


class ContentBasedRecommender:
    def __init__(self, all_grades, user_id, path):
        self.user_grades = [(s[1], s[2]) for s in all_grades if s[0] == int(user_id)]
        self.user_songs = [s[0] for s in self.user_grades]
        self.data = self.read_csv(path)
        self.user_profile = self.get_user_profile()
        self.recommended = self.get_recs()

    def get_user_profile(self):
        feature_matrix = self.data.loc[self.data['nr'].isin(self.user_songs)]
        unique_grades = list(set(self.user_grades))
        user_grades = [s[1] for s in unique_grades]
        m = np.delete(np.array(feature_matrix), 0, 1)
        c = np.array(user_grades)
        weighted_matrix = m * c[:, np.newaxis]
        user_profile = np.sum(weighted_matrix, 0)
        user_profile_norm = user_profile/np.sum(user_profile)
        return user_profile_norm

    def get_recs(self):
        knn = NearestNeighbors(12, p=2)
        knn.fit(self.data)
        user_songs_5 = [s[0] for s in self.user_grades if s[1] == 5]
        if not user_songs_5:
            like_songs = [s[0] for s in self.user_grades if s[1] == 4]
        else:
            like_songs = user_songs_5
        user_data = self.data.loc[self.data['nr'].isin(like_songs)]
        if user_data.empty:
            return pd.DataFrame([], columns=['song_id', 'rec'])
        nn = knn.kneighbors(user_data, return_distance=True)
        result_matrix = []
        dists = nn[0].flatten()
        songs = nn[1].flatten()
        for i in range(0, dists.size):
            result_matrix.append([songs[i], dists[i]])
        df = pd.DataFrame(result_matrix, columns=['song_id', 'rec'])
        #df_sorted = df.sort_values(by=['rec'])
        df_nonzero = df.loc[df['rec'] != 0]
        df_nonzero['rec'] = df_nonzero['rec']*(-1)  # reverse
        scaler = MinMaxScaler()
        df_nonzero['rec'] = scaler.fit_transform(df_nonzero['rec'].values.reshape(-1, 1))
        new_df = pd.DataFrame(df_nonzero.values, columns=['song_id', 'rec'])
        return new_df

    def read_csv(self, path):
        df = pd.read_csv(path)
        df = df[['nr', 'bpm', 'spec flat', 'spec skew', 'kurt', 'zero cross', 'hpss', 'vocal']]
        return df


def main():
    cb = ContentBasedRecommender([[1,1,3],[1,2,4],[1,3,2],[1,4,4],[1,5,2],[1,6,3],[1,7,5],[1,8,3],[1,9,4],[1,10,4],
                                  [1,11,3],[1,12,4],[1,13,3],[1,14,4],[1,15,2],[1,16,2],[1,17,4],[1,18,1],
                                  [1,19,2],[1,20,2],[1,21,3],[1,22,4],[1,23,4],[1,24,3],
                                  [1,25,4],[1,26,4],[1,27,4],[1,28,2]], 1, './data_norm.csv')
    print(cb.recommended)


if __name__ == '__main__':
    main()