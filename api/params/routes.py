from flask import Blueprint, request
from api.extensions import authorized
import json
from .models import ParamUpdate, Param


params = Blueprint("params", __name__, url_prefix="/params")


# Get current params from db/store
@params.route("/get", methods=["POST"])
@authorized
def get():
    if request.method != "POST":
        return "Method not allowed", 405

    return "ok", 200


@params.route("/save", methods=["POST"])
def pull():
    if request.method != "POST":
        return "Method not allowed", 405

    params = request.json

    with open("changes.json", "a") as f:
        f.write(json.dumps(params, sort_keys=False, indent=2))

    return "ok", 200


# Send changes to aws parameter store
@params.route("/store", methods=["POST"])
def store():
    if request.method != "POST":
        return "Method not allowed", 405

    pass
