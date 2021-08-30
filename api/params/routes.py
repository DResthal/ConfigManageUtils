from flask import Blueprint, request
from api.extensions import authorized, conn, ma
import json
from .models import ParamUpdate, Param


params = Blueprint("params", __name__)


# Get current params from db/store
@params.route("/get", methods=["POST"])
@authorized
def get():
    if request.method != "POST":
        return "Method not allowed", 405

    changes = ParamUpdate().query.all()

    return "ok", 200


# Save param changes to db
@params.route("/save", methods=["POST"])
def pull():
    if request.method != "POST":
        return "Method not allowed", 405

    params = request.json

    with open("changes.json", "a") as f:
        f.write(json.dumps(params, sort_keys=False, indent=2))

    return "ok", 200


# save param changes to .json file, add to git and create pr
@params.route("/post", methods=["POST"])
def post():
    pass


# Send changes to aws parameter store
@params.route("/store", methods=["POST"])
def store():
    if request.method != "POST":
        return "Method not allowed", 405

    pass


# Return differences between test and prod
@params.route("/compare", methods=["POST"])
def compare():
    pass
