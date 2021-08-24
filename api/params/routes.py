from flask import Blueprint, request


params = Blueprint("params", __name__)


# Get current params from db/store
@params.route("/get", methods=["POST"])
def get():
    if request.method != "POST":
        return "Method not allowed", 405

    pass


# Save changes to db
@params.route("/post", methods=["POST"])
def post():
    if request.method != "POST":
        return "Method not allowed", 405

    pass


# Git clone > git branch > write changes to file.json > git add > git commit > git push > create pull request
@params.route("/pull", methods=["POST"])
def pull():
    if request.method != "POST":
        return "Method not allowed", 405

    pass


# Send changes to aws parameter store
@params.route("/store", methods=["POST"])
def store():
    if request.method != "POST":
        return "Method not allowed", 405

    pass
