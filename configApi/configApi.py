from flask import Flask, jsonify, request
from fileUtils import file, aws
from gitUtils import git
from dotenv import load_dotenv
from apilogger import CustomLogger
from datetime import datetime
import config
import json
import logging
import os

app = Flask(__name__)
app.config.from_object(config.Dev)
load_dotenv()
t_filepath = "git_repo/example.yml"


# Logger Setup
app_log = CustomLogger(
    name="application_log", log_file="logs/application.log", level=logging.INFO
).create_logger()

err_log = CustomLogger(
    name="error_log", log_file="logs/error.log", level=logging.WARNING
).create_logger()

git_log = CustomLogger(
    name="git_log", log_file="logs/git.log", level=logging.INFO
).create_logger()

app_log.info("Application started.")


def is_json_allowed(data: dict) -> tuple:
    """Checks JSON for specified values and returns
    a tuple containing a message and status code in str and int form respectively.
    The return value of this function can be directly returned by Flask if necessary.

    data: entire JSON from request.json

    Returns (msg: str, status: int)
    """
    # Check for authToken
    try:
        authToken = data["authToken"]
    except KeyError as e:
        err_log.warning(e)
        err_log.warning("No authToken")
        return ("No authToken", 400)

    # Check for userName
    try:
        userName = data["userInfo"]["userName"]
    except KeyError as e:
        err_log.warning(e)
        err_log.warning("No userName")
        return ("No userName", 400)

        # Check for env
        try:
            userName = data["env"]
        except KeyError as e:
            err_log.warning(e)
            err_log.warning("No env")
            return ("No env", 400)

    return ("JSON response accepted", 200)


def which_env(data: str) -> tuple:
    """Returns a tuple whose contents are dependent on
    which env tag was provided in the request.json.
    Returns None if env is invalid.

    data: authToken from request.json['authToken']

    Return (git_uri, filename)
    """
    data = json.loads(data)
    env = data["env"]

    if env == "test":
        git_uri = os.getenv("TEST_REPO_URI")
        filename = os.getenv("TEST_FILENAME")
    elif env == "prod":
        git_uri = os.getenv("PROD_REPO_URI")
        filename = os.getenv("PROD_FILENAME")
    else:
        return None

    return (git_uri, filename)


def token_is_valid(authToken: str) -> bool:
    """Checks supplied authToken against the defined "master" authToken.
    Returns True if tokens match and false if not.

    authToken: Str authToken from request.json
    """
    if authToken != os.getenv("JSON_AUTH_TOKEN"):
        return False
    else:
        return True


@app.route("/getParams", methods=["POST"])
def getParams():
    # Log the endpoint access
    app_log.info(f"Request made to /getParams. \n {request.json}")

    # Check that is_json_allowed is "OK"
    msg, status = is_json_allowed(request.json)

    if status != 200:
        return (msg, status)

    # Validate authToken
    if not token_is_valid(request.json["authToken"]):
        return ("Token is not valid. Please provide a valid authToken", 403)

    # Get env
    git_uri, filename = which_env(request.json["env"])

    # Validate env
    if git_uri is None:
        return ("Invalid env", 400)

    # Generate local directory name
    target_dir = (
        f"{request.json['env']}-repo-{request.json['userInfo']['userName']}"
    )

    # Ensure that the local directory does not exist
    if git.dirname_exists(target_dir):
        return (
            f"Unable to remove {target_dir}. Please contact your admin.",
            500,
        )

    # Clone the repository
    try:
        git.clone(uri=git_uri, target=target_dir)
        app_log.info(f"Repository has been cloned to {target_dir}.")
    except:
        return (
            "Unable to clone repository. Refer to error.log for more details.",
            505,
        )

    # Read the file
    try:
        app_log.info(
            f"Reading file contents. User: {request.json['userInfo']['userName']}"
        )
        data = file.read_yaml(f"{target_dir}/{filename}")
        return jsonify(json.loads(data)), 200
    except:
        msg = "There appears to be an issue reading the yaml file. Refer to error.log for more details"
        return (msg, 500)


@app.route("/putParams", methods=["POST"])
def putParams():
    # Log endpoint access
    app_log.info(f"Request made to /putParams. \n {request.json}")

    # Check that is_json_allowed is "OK"
    msg, status = is_json_allowed(request.json)

    if status != 200:
        return msg, status

    if not token_is_valid(request.json["authToken"]):
        app_log.info(f"Unauthorized request at /putParams. {request.json}")
        return "Invalid authToken. This incident has been logged.", 403
    else:
        now = datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        data = request.json
        params = data["parameters"]
        user = data["userInfo"]
        title = f"Config Change - {now}"
        msg = f"Created by: {user['userName']} at {now}"
        params = file.check_secret(json.dumps(params), delete=True)
        # Git Functions Required Order
        # 1. Switch to main
        # 2. git pull
        # 3. git checkout -b <random branch name>
        # 4. Update file
        # 5. Add and commit new file
        # 6. Create PR
        # Switching back to main after PR is unecessary now
        git.reset_to_main("git_repo")
        git.pull("git_repo")
        branch = git.new_branch("git_repo")
        file.write_file(params, "git_repo/example.yml")
        git.add_commit(
            "git_repo",
            ["example.yml"],
            "Update to example.yml parameters",
            user["userName"],
            user["userEmail"],
        )
        git.create_pr(
            "devblueray/TestConfigs",
            "git_repo",
            os.getenv("ACCESS_TOKEN"),
            title,
            msg,
            branch,
            "main",
        )
        return (
            jsonify({"fileUpdate": "Success", "Add and Commit": "Success"}),
            200,
        )


@app.route("/storeParams", methods=["POST"])
def storeParams():
    msg, status = is_json_allowed(request.json)
    if status != 200:
        return msg, status

    authToken = request.json["authToken"]
    prefix = request.json["prefix"]
    if authToken == os.getenv("AUTH_TOKEN"):
        data = file.read_yaml(t_filepath)
        res = aws.store(data, prefix)
        msg = {}
        for i in res:
            n = 1
            msg[n] = i
            n += 1

        return jsonify(msg), 200
    else:
        return "Invalid Auth Token", 403


if __name__ == "__main__":
    port = 8000
    app.run(debug=True, port=port)

"""
# Example JSON response from client

{
  "authToken": "FXbWZBmGstqCJP8D7P3kzguthu479dFv",
  "userInfo": {
    "userName": "Bob Pickles",
    "userEmail": "bob@pickles.com"
  },
  "env": "test",
  "parameters": {
    "a": {
      "value": "some dumb value",
      "secret": true,
      "comment": "some dumb comment"
    },
    "b": {
      "value": "another dumb value",
      "secret": false,
      "comment": "another dumb comment"
    }
  }
}
"""
