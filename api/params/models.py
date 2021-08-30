from api.extensions import conn, ma
from datetime import datetime

db = conn


class ParamUpdate(db.Model):
    __tablename__ = "paramupdates"

    id = db.Column(db.Integer(), primary_key=True)
    datetime = db.Column(db.DateTime(), default=datetime.utcnow())
    username = db.Column(db.String(30), nullable=False)
    value = db.Column(db.String(60), nullable=False)
    secret = db.Column(db.Boolean, nullable=False)
    comment = db.Column(db.Text, nullable=True)


class Param(db.Model):
    __tablename__ = "params"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    value = db.Column(db.String(30), nullable=False)
    secret = db.Column(db.Boolean, nullable=False)
