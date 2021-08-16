# import git
from flask import app, current_app, request, session
from json import JSONDecodeError
import logging
import json
import git
import os


app_log = logging.getLogger("applog")
err_log = logging.getLogger("errlog")


def check_dir_exists():
    pass


def check_env():
    """Checks the request.json for an env key.
    If present, sets the session.gitrepo to the correct repository."""

    try:
        env = request.json["env"]
    except JSONDecodeError as e:
        app_log(
            f"No env in JSON. \n{json.dumps(request.json, indent=2, sort_keys=False)}\n{e}"
        )
        return "No env", 400

    if env.lower() == "test":
        session["gitrepo"] = current_app.config["TESTREPO"]

    if env.lower() == "prod":
        session["gitrepo"] = current_app.config["PRODREPO"]

    return None


def clone():
    """Clones the proper git repo, based on the sessin gitrepo variable and userName"""
    remote = f"https://{current_app.config['GITHUB_TOKEN']}:x-oauth-basic@github.com/{session['gitrepo']}"
    local_dir = os.path.join(
        current_app.instance_path, f'{/session["userName"]}'
    )
    repo = git.Repo()
    repo.clone_from(url=remote, to_path=local_dir)
    pass
