from __init__ import db

class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    grade = db.relationship('Grades', backref='user_grade', lazy='dynamic')

    def __repr__(self):
        return "User( " + {self.pseudo} + ", " + {self.age} + ", " + {self.gender} + ")"


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    src = db.Column(db.String(255), nullable=False)
    img = db.Column(db.Binary, nullable=False)
    song_meta = db.relationship('Metadata', backref='song_meta', lazy='dynamic')
    song_grade = db.relationship('Grades', backref='song_grade', lazy='dynamic')


class Grades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Integer, nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user_data.id'))


class Metadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # song = db.relationship('Song', backref='song_id', lazy=True)
    title = db.Column(db.String(255), nullable=False)
    band = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(255))
    album = db.Column(db.String(255))
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'))



