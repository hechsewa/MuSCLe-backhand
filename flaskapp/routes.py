import io
import re

import sqlalchemy
from flask import render_template, jsonify, send_file, request, json
from backhand.flaskapp import app, models, db


# home page
from backhand.flaskapp.models import Grades
from backhand.src.crossdomain import crossdomain


@app.route('/')
@app.route('/home')
def homepage():
    return render_template('home.html')


# get the song metadata
@app.route('/meta/<song_id>')
def metadata(song_id):
    meta = models.Metadata.query.get(song_id)
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
    pic = models.Song.query.get(song_id)
    bytes = io.BytesIO(pic.img)
    filename = "cover"+str(song_id)+".jpg"

    return send_file(
        bytes,
        mimetype='image/jpeg')

# get the song feature
@app.route('/feature/<song_id>/<feature_id>')
def feature(song_id, feature_id):
    return 0

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
            grader = Grades(user_id=userid, song_id=songid, grade=gradval)
            db.session.add(grader)
            db.session.flush()
            ret = {"grade_id": grader.id};
            db.session.commit()
            return jsonify(ret)

        else:
            ret = {'status': 'ok'}
            return jsonify(ret)

    except sqlalchemy.exc.IntegrityError:  # if it already exists then smth
        ret = {'status': '400'}
        return jsonify(ret)


# add new user
@app.route('/user/<user_id>', methods=['POST', 'GET'])
@crossdomain(origin='*')
def new_user(user_id):
    try:
        if request.method == 'GET':
            user = models.UserData.query.get(user_id)
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
            user = models.UserData(pseudo=pseudo, age=age, gender=gen)
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
