from flask import Blueprint, request
from flask import current_app
from api.extensions import db, basic_auth
import json
from .models import *
import sys
from logging import getLogger
from sqlalchemy.exc import IntegrityError
from .functions import enc, dec


params = Blueprint("params", __name__)
err_log = getLogger("elog")
app_log = getLogger("alog")
basic_auth.init_app(current_app)


def redacted(data: list) -> list:
    for i in data:
        if i["secret"]:
            i["value"] = "REDACTED"

    return data


# Get current params from db
@basic_auth.required
@params.route("/getparams", methods=["POST"])
def get():
    try:
        params = Params.query.all()
    except:
        err_log.warning(sys.exc_info())
        return "Unable to query params", 500

    params_schema = ParamsSchema(many=True)

    return json.dumps(redacted(json.loads(params_schema.dumps(params)))), 200


@basic_auth.required
@params.route("/getupdates", methods=["POST"])
def get_updates():
    try:
        updates = Updates.query.all()
    except:
        err_log.warning(sys.exc_info())
        return "Unable to query updates", 500

    updates_schema = UpdatesSchema(many=True)

    return json.dumps(redacted(json.loads(updates_schema.dumps(updates)))), 200


# Save param changes to db
@basic_auth.required
@params.route("/save", methods=["POST"])
def save():
    try:
        user_info = request.json["userInfo"]
    except json.JSONDecodeError as e:
        err_log.warning(e)
        return "Invalid request content", 404

    try:
        param_updates = request.json["parameters"]
    except json.JSONDecodeError as e:
        err_log.warning(e)
        return "Inavalide request content", 404

    updates_list = []

    for p in param_updates:

        if p["secret"]:
            p["value"] = enc(p["value"])

        try:
            update = {
                "username": user_info["userName"],
                "useremail": user_info["userEmail"],
                "name": p["name"],
                "prefix": p["prefix"],
                "value": p["value"],
                "secret": p["secret"],
                "comment": p["comment"],
            }
        except json.JSONDecodeError as e:
            err_log.warning(e)
            return "Unable to create update dict, likely missing fields", 404

        updates_list.append(update)

        try:
            param = {
                "name": p["name"],
                "prefix": p["prefix"],
                "value": p["value"],
                "secret": p["secret"],
                "comment": p["comment"],
            }
        except json.JSONDecodeError as e:
            err_log.warning(e)
            return (
                """Unable to create parameter dict, likely missing fields. 
                \nThis error should never exist, if you see this, something has gone terribly wrong!!! 
                \nPlease contact the administrator and/or developer(s)""",
                404,
            )

        app_log.info(json.dumps(update, sort_keys=True, indent=4))
        app_log.info(json.dumps(param, sort_keys=True, indent=4))

        try:
            new_update = Updates(**update)
            db.session.add(new_update)
            db.session.commit()
            app_log.info("Database entry created on table: updates")
        except:
            err_log.warning(sys.exc_info())
            return "Unable to save updates to database", 500

        if Params.query.get((param["name"], param["prefix"])):
            existing_param = Params.query.get((param["name"], param["prefix"]))
            existing_param.value = param["value"]
            existing_param.secret = param["secret"]
            existing_param.comment = param["comment"]
            db.session.commit()
            return "Updated", 202
        else:
            new_param = Params(**param)
            db.session.add(new_param)
            db.session.commit()
            return "Created", 201

    return json.dumps(redacted(updates_list)), 200


# save param changes to .json file, add to git and create pr
@basic_auth.required
@params.route("/post", methods=["POST"])
def post():
    params = Params.query.all()
    params_schema = ParamsSchema(many=True)

    with open("params.json", "w") as f:
        f.write(params_schema.dumps(params, sort_keys=True, indent=4))

    return "ok", 200


# Send changes to aws parameter store
@basic_auth.required
@params.route("/store", methods=["POST"])
def store():
    pass


# Copy all parameters from an existing prefix to a new prefix, ignoring those which currently exist
@basic_auth.required
@params.route("/copysprint", methods=["POST"])
def copysprint():
    pass


# This route temporarily exists as a place to test functions
@params.route("/test", methods=["GET"])
def test():
    return "OK", 200
