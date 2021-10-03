from flask import request, current_app
from logging import getLogger
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_basicauth import BasicAuth


e_log = getLogger("elog")
a_log = getLogger("alog")

db = SQLAlchemy()
ma = Marshmallow()
basic_auth = BasicAuth()


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
