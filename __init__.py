import os
import click
from flask import Flask
from flask.cli import with_appcontext
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://siogaomlorkjzp:bf59ed280c5de6981e2bad8078f123a4400687968f1d24ceebbf6d1c13335a17@ec2-46-137-120-243.eu-west-1.compute.amazonaws.com:5432/ddbumffp5cq5ki'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://3wvzLcjQzD:RArEPgAhKS@remotemysql.com:3306/3wvzLcjQzD'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)


@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()


app.cli.add_command(create_tables)
