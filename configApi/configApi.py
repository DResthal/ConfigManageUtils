from flask import Flask, jsonify, request
from fileUtils import file, aws
from gitUtils import git
from dotenv import load_dotenv
from apilogger import CustomLogger
from datetime import datetime
import traceback
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


@app.route("/getParams", methods=["POST"])
def getParams():
    # Check for authToken
    if request.json["authToken"]:
        authToken = request.json["authToken"]
    else:
        msg = "No authToken"
        app_log.info(msg)
        return msg, 403

    # Check for env
    if request.json["env"]:
        env = request.json["env"]
    else:
        err_log.warning("No env tag")
        return "No env tag", 400

    # Check which env
    if env == "test":
        repository_uri = os.getenv("TEST_REPO_URI")
    elif env == "prod":
        repository_uri = os.getenv("PROD_REPO_URI")
    else:
        msg = "Invalid env, please specify 'prod' or 'test'. env={env}"
        err_log.warning(msg)
        return msg, 400

    app_log.info(f"/getParams request: authToken={authToken}, env={env}")

    # Check authToken is valid
    if authToken == os.getenv("JSON_EX_AUTH_TOKEN"):
        app_log.info("Auth token accepted.")
        target = f"{env}-repository-{request.json['userInfo']['userName']}"

        # Check directory name does not exist or was removed
        if git.dirname_exists(target):
            err_log.warning(
                f"Unable to remove {target} directory. Cannot clone directory."
            )
            return (
                f"Directory {target} exists and cannot be removed. Cloning cannot proceed. Please see error.log for more details.",
                500,
            )

        # Run git clone
        try:
            git.clone(
                uri=repository_uri,
                target=target,
                token=os.getenv("ACCESS_TOKEN"),
            )
            app_log.info(f"Repository cloned to {target}")
        except:
            return "Unable to clone repository. Please read error.log for more details."

        # Read yaml file and return JSON
        try:
            data = file.read_yaml(f"{target}/example.yml")
            return jsonify(json.loads(data)), 200
        except:
            msg = "There appears to not be a yaml file, or the yaml file contains errors that cannot be parsed."
            err = traceback.format_exc()
            err_log.warning(msg)
            err_log.warning(err)
            return msg, 500
    else:
        msg = (
            f"Invalid authToken supplied to getParams. authToken = {authToken}"
        )
        err_log.warning(msg)
        return msg, 403


@app.route("/putParams", methods=["POST"])
def putParams():
    authToken = request.json["authToken"]
    if authToken == os.getenv("AUTH_TOKEN"):
        now = datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        data = request.json
        params = data["parameters"]
        user = data["userInfo"]
        title = f"Config Change - {now}"
        msg = f"Created by: {user['userName']} at {now}"
        params = file.check_secret(json.dumps(params), delete=True)
        # Git Functions
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
    else:
        return "Invalid Auth Token", 403


@app.route("/storeParams", methods=["POST"])
def storeParams():
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
