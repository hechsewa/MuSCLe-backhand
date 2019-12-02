import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler


class CollaborativeFilteringRecommender:
    def __init__(self, all_grades, user_id):
        self.all_grades = all_grades
        self.user_id = user_id
        self.trening_data = [s for s in self.all_grades if not s[0] == int(self.user_id)]
        self.user_profile = self.get_user_profile()
        self.item_sim_df = self.preprocess_data()
        self.recommended = self.get_recommendations()

    def normalization(self, row):
        return (row-row.mean())/(row.max() - row.min())

    def preprocess_data(self):
        if not self.trening_data:
            return pd.DataFrame()
        rows = np.unique([s[0] for s in self.trening_data])
        columns = np.array(list(range(1,108)))
        data = np.zeros((rows.size, columns.size))
        #  fill data matrix
        i=0
        for u in rows:  # for each user
            user_grades = []
            for song in columns:  # check if they graded the song
                grade = [s[2] for s in self.trening_data if s[0] == u and s[1] == song]
                if not grade:
                    user_grades.append(0)
                else:
                    user_grades.append(grade[0])
            data[i] = user_grades
            i += 1

        df = pd.DataFrame(data=data, index=rows, columns=columns)
        ratings_std = df
        item_sim = cosine_similarity(ratings_std.T)
        item_sim_df = pd.DataFrame(item_sim, index=ratings_std.columns, columns=ratings_std.columns)
        return item_sim_df

    def get_similar_song(self, song, rating):
        similarity = self.item_sim_df[song]*(rating-2.5)
        similarity = similarity.sort_values(ascending=False)
        return similarity

    # [[user_id, song_id, rating],[].., []]
    def get_user_profile(self):
        user = [(s[1], s[2]) for s in self.all_grades if s[0] == int(self.user_id)]
        return user

    def get_recommendations(self):
        similar_songs = pd.DataFrame()
        if self.item_sim_df.empty:
            return similar_songs
        for song, rating in self.user_profile:
            similar_songs = similar_songs.append(self.get_similar_song(song, rating), ignore_index=True)
        user_songs = np.unique([i[0] for i in self.user_profile])
        sim = similar_songs.sum().sort_values(ascending=False)
        rec = sim.drop(user_songs)
        if not self.user_profile:
            return pd.DataFrame()
        data = {'song_id': rec.index.values, 'rec': rec.values}
        df = pd.DataFrame(data, columns=['song_id', 'rec'])
        scaler = MinMaxScaler()
        df['rec'] = scaler.fit_transform(df['rec'].values.reshape(-1, 1))
        return df


def main():
    cb = CollaborativeFilteringRecommender([[2, 1, 5], [2, 2, 5], [2, 3, 2], [2, 4, 1], [2,5,2],[1,1,3],[1,2,4],[1,3,2],[1,4,4],[1,5,2],[1,6,3],[1,7,5],[1,8,3],[1,9,4],[1,10,4],
                                  [1,11,3],[1,12,4],[1,13,3],[1,14,4],[1,15,2],[1,16,2],[1,17,4],[1,18,1],
                                  [1,19,2],[1,20,2],[1,21,3],[1,22,4],[1,23,4],[1,24,3],
                                  [1,25,4],[1,26,4],[1,27,4],[1,28,2], [3,1,5],[3,2,4],[3,3,2],[3,4,4],[3,5,2],[3,6,3],[3,7,5],[3,8,3],[3,9,4],[3,10,4],
                                  [3,11,1],[3,12,3],[3,13,3],[3,14,5],[3,15,4],[3,16,2],[3,17,4],[3,18,1],
                                  [3,19,1],[3,20,3],[3,21,3],[3,22,4],[3,23,4],[3,24,3],
                                  [3,25,1],[3,26,4],[3,27,4],[3,28,2]], 2)
    print(cb.recommended)

if __name__ == '__main__':
    main()