from flask import Flask, jsonify, request
from fileUtils import file, aws
from gitUtils import git
from dotenv import load_dotenv
from apilogger import CustomLogger
from datetime import datetime
import json
import logging
import os

app = Flask(__name__)
load_dotenv()
t_filepath = "git_repo/example.yml"

if not os.path.exists("configApi/logs"):
    os.mkdir("configApi/logs")

e_log = CustomLogger(
    "e_log", "configApi/logs/error.log", level=logging.DEBUG
).create_logger()
a_log = CustomLogger(
    "a_log", "configApi/logs/app.log", level=logging.INFO
).create_logger()


@app.route("/getParams", methods=["POST"])
def getParams():
    authToken = request.json["authToken"]
    if authToken == os.getenv("AUTH_TOKEN"):
        git.clone(
            uri="github.com/devblueray/TestConfigs",
            target="git_repo",
            token=os.getenv("ACCESS_TOKEN"),
        )
        data = file.read_yaml("git_repo/example.yml")
        a_log.info("Repository cloned and data decrypted.")
        return jsonify(json.loads(data)), 200
    else:
        return "Invalid Auth Token", 403


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
    a_log.info(f"Server started and running on port {port}")

"""
# Example JSON response from client

    {
    "authToken": "abc123",
    "userInfo": {
        "userName": "Bob Pickles",
        "userEmail": "bob@pickles.com"
    },
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
