from flask import Flask, jsonify

# from fileUtils import file
from gitUtils import git
from dotenv import load_dotenv
from apilogger import CustomLogger
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
    return "Cloned repository", 200


@app.route("/putParams")
def putParams():
    # Save JSON to yml and perform git actions
    pass


if __name__ == "__main__":
    app.run(debug=True)
