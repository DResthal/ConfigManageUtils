from flask import Blueprint, request
from api.extensions import authorized, db, ma
import json
from .models import Updates, Params, UpdatesSchema, ParamsSchema
import sys
from logging import getLogger


params = Blueprint("params", __name__)
err_log = getLogger("elog")
app_log = getLogger("alog")
 
# Get current params from db
@params.route("/getparams", methods=["POST"])
@authorized
def get():
        try:
            params = Params.query.all()
        except:
            err_log.warning(sys.exc_info())
            return "Unable to query params", 500

        params_schema = ParamsSchema(many=True)

        return params_schema.dumps(params, many=True), 200

@params.route("/getupdates", methods=["POST"])
@authorized
def get_updates():
    try:
        updates = Updates.query.all()
    except:
        err_log.warning(sys.exc_info())
        return "Unable to query updates", 500

    updates_schema = UpdatesSchema(many=True)

    return updates_schema.dumps(updates), 200

# Save param changes to db
@params.route("/save", methods=["POST"])
def pull():
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

    for p in param_updates:
        update = {
            "username":user_info["userName"],
            "useremail":user_info["userEmail"],
            "name":p["name"],
            "value":p["value"],
            "secret":p["secret"],
            "comment":p["comment"]
        }

        try:
            new_update = Updates(**update)
        except:
            err_log.warning(sys.exc_info())
            return "Unable to create instance of Updates table entry", 500

        try:
            db.session.add(new_update)
            db.session.commit()
        except:
            err_log.warning(sys.exc_info())
            return "Unable to save to databases", 500

    return "OK", 200

# save param changes to .json file, add to git and create pr
@authorized
@params.route("/post", methods=["POST"])
def post():
    params = Params.query.all()
    params_schema = ParamsSchema(many=True)

    with open("params.json", "w") as f:
        f.write(params_schema.dumps(params, sort_keys=True, indent=4))

    return "ok", 200


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
