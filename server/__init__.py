import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import ModelSchema


# app.config['SECRET_KEY'] = 'mysecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://tinyfee4_Team:k-k)6ih8URbs@162.241.219.131/tinyfee4_sources'
app.config["SQLALCHEMY_POOL_RECYCLE"] = 280
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'secret'
# :3306
db = SQLAlchemy(app)
ma = Marshmallow(app)


# -------------------------------- Blueprints -------------------------------- #
# Must be defined after db
from server.emissions.views import emissions_blueprint
app.register_blueprint(emissions_blueprint,url_prefix="/emissions")

from server.solutions.views import solutions_blueprint
app.register_blueprint(solutions_blueprint,url_prefix="")
