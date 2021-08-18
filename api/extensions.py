import json
from flask import request, g, current_app
from flask.cli import with_appcontext
import click
from logging import getLogger
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


e_log = getLogger("elog")
a_log = getLogger("alog")
conn = SQLAlchemy()
ma = Marshmallow()


def authorized(func):
    @wraps(func)
    def auth_wrapper(*args, **kwargs):
        data = request.json

        if not data["authToken"]:
            return "Not Allowed", 403

        if not data["userInfo"]["userName"]:
            return "Not Allowed", 403

        if data["authToken"] != current_app.config["AUTHTOKEN"]:
            return "Not Allowed", 403

        return func(*args, **kwargs)

    return auth_wrapper


@click.command("create-db")
@with_appcontext
def create_db():
    db.create_all()
    click.echo("Tables created.")


def add_app(app):
    app.cli.add_command(create_db)
