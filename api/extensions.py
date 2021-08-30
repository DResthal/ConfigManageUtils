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
            return "Unauthorized", 402

        if data["authToken"] != current_app.config["AUTHTOKEN"]:
            return "Unauthorized", 402

        return func(*args, **kwargs)

    return auth_wrapper


def env_req(func):
    @wraps(func)
    def env_wrapper(*args, **kwargs):
        data = request.json

        if not data["env"]:
            return "env Required", 402

        return func(*args, **kwargs)

    return env_wrapper


@click.command("create-conn")
@with_appcontext
def create_conn():
    conn.create_all()
    click.echo("Tables created.")


def add_app(app):
    app.cli.add_command(create_conn)
