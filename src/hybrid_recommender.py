#from src.collaborative_filtering_recommender import CollaborativeFilteringRecommender
#from src.content_based_recommender import ContentBasedRecommender
import pandas as pd
from src.collaborative_filtering_recommender import CollaborativeFilteringRecommender
from src.content_based_recommender import ContentBasedRecommender
from sklearn.preprocessing import MinMaxScaler


class HybridRecommender:
    def __init__(self, all_grades, path, user_id):
        self.cf_rec = CollaborativeFilteringRecommender(all_grades, user_id)
        self.cb_rec = ContentBasedRecommender(all_grades, user_id, path)
        self.user_songs = [s[1] for s in all_grades if s[0] == int(user_id)]
        self.recommended = self.recommend()

    def recommend(self):
        # get top 100 cf recommendations from cb and cf recommenders
        cf_df = self.cf_rec.recommended.rename(columns={'rec': 'recCF'})
        cb_df = self.cb_rec.recommended.rename(columns={'rec': 'recCB'})
        if not cf_df.empty:
            recs_df = cf_df.merge(cb_df,
                                  how='outer',
                                  left_on='song_id',
                                  right_on='song_id')
            recs_df = recs_df.fillna(0)
            print(recs_df)
            # Computing a hybrid recommendation score based on CF and CB scores
            recs_df['recHybrid'] = recs_df['recCF'] + recs_df['recCB']
            recs_df = recs_df.drop_duplicates(subset='song_id')
            recs_df = recs_df.loc[~recs_df['song_id'].isin(self.user_songs)]
            scaler = MinMaxScaler()
            recs_df['recHybrid'] = scaler.fit_transform(recs_df['recHybrid'].values.reshape(-1, 1))
            recs = recs_df.sort_values('recHybrid', ascending=False).head(10)
            new = recs[['song_id', 'recHybrid']].copy()
            print(new)
            return new
        else:
            return cb_df.rename(columns={'recCB': 'recHybrid'})


def main():
    hyb = HybridRecommender([[2, 1, 5], [2, 2, 5], [2, 3, 2], [2, 4, 1], [2,5,2],[1,1,3],[1,2,4],[1,3,2],[1,4,4],[1,5,2],[1,6,3],[1,7,5],[1,8,3],[1,9,4],[1,10,4],
                                  [1,11,3],[1,12,4],[1,13,3],[1,14,4],[1,15,2],[1,16,2],[1,17,4],[1,18,1],
                                  [1,19,2],[1,20,2],[1,21,3],[1,22,4],[1,23,4],[1,24,3],
                                  [1,25,4],[1,26,4],[1,27,4],[1,28,2], [3,1,5],[3,2,4],[3,3,2],[3,4,4],[3,5,2],[3,6,3],[3,7,5],[3,8,3],[3,9,4],[3,10,4],
                                  [3,11,1],[3,12,3],[3,13,3],[3,14,5],[3,15,4],[3,16,2],[3,17,4],[3,18,1],
                                  [3,19,1],[3,20,3],[3,21,3],[3,22,4],[3,23,4],[3,24,3],
                                  [3,25,1],[3,26,4],[3,27,4],[3,28,2]],
                            './data.csv', 2)
    print(hyb.recommended)


if __name__ == '__main__':
    main()
