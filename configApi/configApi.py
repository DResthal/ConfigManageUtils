from flask import Flask, jsonify, request
from fileUtils import file, aws
from gitUtils import git
from dotenv import load_dotenv
from apilogger import CustomLogger
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


def which_env(env: str) -> tuple:
    """Returns a tuple whose contents are dependent on
    which env tag was provided in the request.json.
    Returns None if env is invalid.

    env: string of env from request.json

    Return (git_uri, filename)
    """
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


def generate_directory_name(data: dict) -> str:
    """Generates the local directory name for the git repo
    based on the env and userName supplied.

    data: Dict containing either env and userInfo : { userName : }
    or the entire request.json

    This function should NEVER fail, because it should always be called AFTER
    is_json_allowed returns 200, OK and never upon any other result of is_json_allowed.
    Therefore, no error checking should be included here as errors should be caught
    before this function is ever invoked.
    """
    target_dir = f"{data['env']}-repo-{data['userInfo']['userName']}"
    return target_dir


@app.route("/getParams", methods=["POST"])
def getParams():
    # Log the endpoint access
    app_log.info(f"Request made to /getParams. \n {request.json}")

    # Check that is_json_allowed is "OK"
    msg, status = is_json_allowed(request.json)

    if status != 200:
        return (msg, status)

    # Validate authToken before proceeding
    if not token_is_valid(request.json["authToken"]):
        return ("Token is not valid. Please provide a valid authToken", 403)

    # Get env
    git_uri, filename = which_env(request.json["env"])

    # Validate env
    if git_uri is None:
        return ("Invalid env", 400)

    # Generate directory name
    target_dir = generate_directory_name(request.json)

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

    # Validate authToken before proceeding
    if not token_is_valid(request.json["authToken"]):
        app_log.info(f"Unauthorized request at /putParams. {request.json}")
        return "Invalid authToken. This incident has been logged.", 403

    # Get filename based on env
    git_uri, filename = which_env(request.json["env"])

    # Generate directory name
    target_dir = generate_directory_name(request.json)

    # Checking that the directory name generated is present, if not, the request was bad.
    if not os.path.exists(target_dir):
        err_log.warning(
            f"{target_dir} does not exist. Bad JSON request. \n {request.json}"
        )
        return (
            "Something went wrong. Please ensure your authToken, userName and env are the same as when you created your clone.",
            400,
        )

    # Add last modified data to each param
    params = file.last_modified(request.json)

    # Encrypt secret parameters
    enc_params = file.check_secret(json.dumps(params), delete=True)

    # I think that some of this needs to be moved out of putParams
    # I'm thinking that create_pr could be in a cleanup endpoint that also deletes
    # the local directory, called AFTER storeParams.
    # Required Order of Git Functions
    # 1. Switch to main
    # 2. git pull
    # 3. git checkout -b <random branch name>
    # 4. Update file
    # 5. Add and commit new file
    # 6. Create PR
    # Switching back to main after PR is unecessary now
    # These notes have too much future chaos potential to remove.
    git.reset_to_main(target_dir)
    git.pull(target_dir)
    new_branch = git.new_branch(target_dir)
    file.write_file(enc_params, filename=f"{target_dir}/{filename}")
    git.add_commit(
        target_dir,
        [filename],
        "Updated yaml parameters",
        request.json["userInfo"]["userName"],
        request.json["userInfo"]["userEmail"],
    )
    git.create_pr(
        uri=git_uri,
        user=request.json["userInfo"]["userName"],
        dir=target_dir,
        branch_name=new_branch,
    )

    app_log.info(f"Created PR for {git_uri}")
    return "PR Created", 200


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
