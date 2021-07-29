import json
from flask import request, g, current_app
from logging import getLogger
from functools import wraps

e_log = getLogger("elog")
a_log = getLogger("alog")


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
