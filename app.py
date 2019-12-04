import io
import re
import sqlalchemy
from flask import render_template, jsonify, send_file, request, json, Flask, url_for
from sqlalchemy import select
from models import Grades, Metadata, Song, UserData, Recommendations # przy deploy wziąc ta kropke wywalic
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from __init__ import app, db
from src.hybrid_recommender import HybridRecommender


@app.route('/')
@app.route('/home')
def homepage():
    return render_template('home.html')


@app.route('/finish')
def finish():
    db.session.close()
    db.dispose()
    return jsonify({"status": "ok"})

# get the song metadata
@app.route('/meta/<song_id>')
def metadata(song_id):
    meta = Metadata.query.get(song_id)
    genre = re.sub('[\(+(0-9)\)]', '', meta.genre)
    ret = {"title": meta.title,
           "band": meta.band,
           "genre": genre,
           "album": meta.album
           }
    return jsonify(ret)


#get the song pic
@app.route('/pic/cover<song_id>.jpg')
def cover(song_id):
    pic = Song.query.get(song_id)
    if not pic:
        return jsonify({"status": "ok"})
    bytes = io.BytesIO(pic.img)
    filename = "cover"+str(song_id)+".jpg"

    return send_file(
        bytes,
        mimetype='image/jpeg')

# recommend a song
@app.route('/user/<user_id>/recommend')
def recommend(user_id):
    # get all grades like: [[user_id, song_id, grade]]
    data = Grades.query.with_entities(Grades.user_id, Grades.song_id, Grades.grade).all()
    df_csv = "static/data.csv"
    hyb_rec = HybridRecommender(data, df_csv, user_id)
    hyb_df = hyb_rec.recommended.values.tolist()
    # save the recommendation to recommendations table
    counter = len([x for x in data if x[0] == int(user_id)])
    recs = Recommendations.query \
        .filter_by(user_id=user_id) \
        .order_by(Recommendations.rec_score.desc()) \
        .with_entities(Recommendations.rec_song_id) \
        .all()
    print(counter)
    if counter == 30 and not recs:  # przy 30 ocenie zapisz rekomendacje
        for s in hyb_df:
            print("saving recs to db")
            rec = Recommendations(user_id=user_id, rec_song_id=s[0], rec_score=s[1])
            db.session.add(rec)
            db.session.flush()
            db.session.commit()
        recs = Recommendations.query \
            .filter_by(user_id=user_id) \
            .order_by(Recommendations.rec_score.desc()) \
            .with_entities(Recommendations.rec_song_id) \
            .all()

    print(recs)
    if recs and counter >= 30:
        return jsonify({'song_id': recs[counter-31][0]})
    else:
        return jsonify({'song_id': -1})

# get random song
@app.route('/user/<user_id>/random')
def get_random(user_id):
    # get all users graded songs
    songs = Grades.query.filter_by(user_id=user_id).with_entities(Grades.song_id).all()
    all_songs = list(range(1, 108))
    user_songs = [s[0] for s in songs]
    remaining = [s for s in all_songs if s not in user_songs]
    if remaining:
        return jsonify({'song_id': remaining[0]})
    else:
        return jsonify({'song_id': -1})

# get the user grades
@app.route('/user/<user_id>/grades')
def grades(user_id):
    data = Grades.query.filter_by(user_id=user_id).with_entities(Grades.song_id, Grades.grade).all()
    ret = jsonify(data)
    return ret

# get number of songs graded by user
@app.route('/user/<user_id>/grades/sum')
def grades_sum(user_id):
    data = Grades.query.filter_by(user_id=user_id).with_entities(Grades.song_id, Grades.grade).all()
    ret = {'grade': len(data)}
    return jsonify(ret)

# add new grade or get the grade for user for song
@app.route('/user/<user_id>/song/<song_id>/grade', methods=['GET', 'POST'])
def add_grade(user_id, song_id):
    try:
        if request.method == 'GET':
            users = Grades.query.filter_by(user_id=user_id).all()
            grade = users.filter_by(song_id=song_id).first(1)
            ret = {'status': 'ok'}
            return jsonify(ret)

        if request.method == 'POST':
            content = request.get_json(force=True)
            userid = content.get("user_id")
            songid = content.get("song_id")
            gradval = content.get("grade")
            exsists = Grades.query\
                      .filter_by(user_id=userid)\
                      .filter_by(song_id=songid).all()
            if not exsists:
                grader = Grades(user_id=userid, song_id=songid, grade=gradval)
                db.session.add(grader)
                db.session.flush()
                ret = {"grade_id": grader.id}
                db.session.commit()
                return jsonify(ret)

        ret = {'status': 'ok'}
        return jsonify(ret)

    except sqlalchemy.exc.IntegrityError:  # if it already exists then smth
        ret = {'status': '400'}
        return jsonify(ret)


# add new user
@app.route('/user/<user_id>', methods=['POST', 'GET'])
def new_user(user_id):
    try:
        if request.method == 'GET':
            user = UserData.query.get(user_id)
            ret = {"id": user.id,
                   "pseudo": user.pseudo,
                   "age": user.age,
                   "gender": user.gender
                   }
            return jsonify(ret)

        if request.method == 'POST':
            content = request.get_json(force=True)
            pseudo = str(content.get("pseudo"))
            age = int(content.get("age"))
            gen = str(content.get("grade"))
            user = UserData(pseudo=pseudo, age=age, gender=gen)
            db.session.add(user)  # so this works :)
            db.session.flush()
            ret = {"user_id": user.id}
            db.session.commit()
            return jsonify(ret)
        else:
            ret = {'status': 'ok'}
            return jsonify(ret)

    except sqlalchemy.exc.IntegrityError:  # if it already exists then smth
        ret = {'status': 'not ok'}
        return jsonify(ret)
    ret = {'status': 'ok'}
    return jsonify(ret)


if __name__ == '__main__':
    app.run()
