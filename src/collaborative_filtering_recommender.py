import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


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
        #rows = np.array(list(range(0,108)))
        #columns = np.unique([s[0] for s in self.trening_data])
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
        ratings_std = df #.apply(self.normalization)
        print(ratings_std)
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
        rec_val = np.divide(rec.values-rec.values.mean(), rec.values.max()-rec.values.min())
        data = {'song_id': rec.index.values, 'rec': rec_val}
        df = pd.DataFrame(data, columns=['song_id', 'rec'])
        return df


def main():
    # data = [[user, song, rating], [user, song, rating], []]
    cb = CollaborativeFilteringRecommender([[2, 1, 5], [2, 2, 5], [2, 3, 2], [2, 4, 1], [1,4,2], [1,2,4]], 1)
    print(cb.recommended)
    #cb.get_recommendations()


if __name__ == '__main__':
    main()