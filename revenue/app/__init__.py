from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from revenue.app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from revenue.app.models import Entry


@app.route("/")
def index():
    return jsonify(hello="Hello")


@app.route("/hourly")
def hourly():
    # TODO
    entries = Entry.query.all()
    return jsonify(msg="implement me - {}".format(entries))


@app.route("/daily")
def daily():
    # TODO
    return jsonify(msg="implement me")
