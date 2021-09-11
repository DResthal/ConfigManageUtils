from flask import Blueprint, request
from api.extensions import authorized, db
import json
from .models import Updates, Params, UpdatesSchema, ParamsSchema
import sys
from logging import getLogger


params = Blueprint("params", __name__)
err_log = getLogger("elog")
app_log = getLogger("alog")
 
# Get current params from db
@params.route("/get", methods=["POST"])
@authorized
def get():
        try:
            params = Params.query.all()
        except:
            err_log.warning(sys.exc_info())
            print("Unable to get params from db")
            pass

        params_schema = ParamsSchema(many=True)

        try:
            params_schema.validate(params)
            print(params_schema.validate(params))
        except:
            err_log.warning(sys.exc_info())
            print("Unable to validate data.")
            pass

        return params_schema.dumps(params, many=True), 200

# Save param changes to db
@params.route("/save", methods=["POST"])
def pull():
    
    for r in request.json["parameters"]:
        try:
            new_param = Params(**r)
        except:
            err_log.warning(sys.exc_info())
            pass

        try:
            db.session.add(new_param)
            app_log.info("New parameter added to session")
            db.session.commit()
            app_log.info("Param saved to database")
        except:
            err_log(sys.exc_info())
            pass
        

    return "OK", 200


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
