from flask import Flask, jsonify, request
from fileUtils import file
from gitUtils import git
from dotenv import load_dotenv
from apilogger import CustomLogger
import json
import logging
import os

app = Flask(__name__)
load_dotenv()

e_log = CustomLogger(
    "e_log", "configApi/logs/error.log", level=logging.DEBUG
).create_logger()
a_log = CustomLogger(
    "a_log", "configApi/logs/app.log", level=logging.INFO
).create_logger()


@app.route("/hello")
def hello():
    data = {"message": "It's working!", "author": "Neil", "secret": False}
    return jsonify(data)


@app.route("/getParams")
def getParams():
    git.clone(
        uri="github.com/DralrinResthal/ConfigTestRepo",
        target="git_repo",
        token=os.getenv("ACCESS_TOKEN"),
    )
    data = file.read_yaml("git_repo/example.yml")
    data = file.check_secret(data, decrypt=True)
    a_log.info("Repository cloned and data decrypted.")

    return jsonify(json.loads(data)), 200


@app.route("/putParams", methods=["POST"])
def putParams():
    data = request.json
    params = data["parameters"]
    user = data["userInfo"]
    params = file.check_secret(json.dumps(params))
    file.write_file(params, "git_repo/example.yml")
    git.pull("git_repo")
    branch = git.new_branch("git_repo")
    git.add_commit(
        "git_repo",
        ["example.yml"],
        "Update to example.yml parameters",
        user["userName"],
        user["userEmail"],
    )
    git.create_pr(
        "DralrinResthal/ConfigTestRepo",
        "git_repo",
        os.getenv("ACCESS_TOKEN"),
        "Test Pull Request!",
        "This is the body of my test PR",
        branch,
        "main",
    )
    return jsonify({"fileUpdate": "Success", "Add and Commit": "Success"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=8000)

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
