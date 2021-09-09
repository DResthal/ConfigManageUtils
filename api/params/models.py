from api.extensions import db, ma
from datetime import datetime
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field


class Updates(db.Model):
    __tablename__ = "updates"

    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime(), default=datetime.utcnow())
    username = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(30), nullable=False)
    value = db.Column(db.String(60), nullable=False)
    secret = db.Column(db.Boolean, nullable=False)
    comment = db.Column(db.Text, nullable=True)


class Params(db.Model):
    __tablename__ = "params"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    value = db.Column(db.String(30), nullable=False)
    secret = db.Column(db.Boolean, nullable=False)


class UpdatesSchema(ma.SQLAlchemyAutoSchema):
    class meta:
        model = Updates


class ParamsSchema(ma.SQLAlchemyAutoSchema):
    class meta:
        model = Params
