from api.extensions import db, ma
from datetime import datetime
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class Updates(db.Model):
    __tablename__ = "updates"

    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime(), default=datetime.utcnow())
    prefix = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(30), nullable=False)
    useremail = db.Column(db.String(60), nullable=False)
    name = db.Column(db.String(30), nullable=False)
    value = db.Column(db.String, nullable=False)
    secret = db.Column(db.Boolean, nullable=False)
    comment = db.Column(db.Text, nullable=False, default="")


class Params(db.Model):
    __tablename__ = "params"

    name = db.Column(db.String(30), nullable=False, primary_key=True)
    prefix = db.Column(db.String(30), nullable=False, primary_key=True)
    value = db.Column(db.String, nullable=False)
    secret = db.Column(db.Boolean, nullable=False)
    comment = db.Column(db.Text, nullable=False, default="")


class UpdatesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Updates


class ParamsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Params


def init_db():
    db.create_all()
