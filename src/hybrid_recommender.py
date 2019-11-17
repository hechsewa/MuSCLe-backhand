from src.collaborative_filtering_recommender import CollaborativeFilteringRecommender
from src.content_based_recommender import ContentBasedRecommender


class HybridRecommender:
    def __init__(self, all_grades, path, user_id):
        self.cf_rec = CollaborativeFilteringRecommender(all_grades, user_id)
        self.cb_rec = ContentBasedRecommender(all_grades, user_id, path)
        self.recommended = self.recommend()

    def recommend(self):
        # get top 100 cf recommendations from cb and cf recommenders
        cf_df = self.cf_rec.recommended.rename(columns={'rec': 'recCF'})
        cb_df = self.cb_rec.recommended.rename(columns={'rec': 'recCB'})
        if not cf_df.empty:
            recs_df = cb_df.merge(cf_df,
                                  how='inner',
                                  left_on='song_id',
                                  right_on='song_id')

            # Computing a hybrid recommendation score based on CF and CB scores
            recs_df['recHybrid'] = recs_df['recCF'] + recs_df['recCB']
            recs = recs_df.sort_values('recHybrid', ascending=False).head(10)
            return recs
        else:
            return cb_df.rename(columns={'recCB': 'recHybrid'})


def main():
    hyb = HybridRecommender([[2,1,5], [2,2,5], [2,3,2], [2,4,1]],
                            './data.csv', 2)
    print(hyb.recommended)


if __name__ == '__main__':
    main()
