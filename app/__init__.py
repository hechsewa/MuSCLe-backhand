from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['127.0.0.1:5000'])

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://hechsma2:AWjLUDbZaz2Srh6j@mysql.agh.edu.pl:3306/hechsma2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://3wvzLcjQzD:RArEPgAhKS@remotemysql.com:3306/3wvzLcjQzD'
db = SQLAlchemy(app)

from .app import app
