from dotenv import load_dotenv
from github import Github
import traceback
from git import Actor
from shutil import rmtree
import git
import sys
import os, string, random
import logging

load_dotenv()

token = os.getenv("ACCESS_TOKEN")
git_log = logging.getLogger("git_log")
err_log = logging.getLogger("error_log")


def dirname_exists(dirname: str) -> bool:
    """Check if the dirname specified exists.
    If so, delete that dirname so that the repository can be cloned properly

    dirname: String name of directory

    returns True if directory exists and cannot be removed,
    False if directory does not exist or exists and was removed.
    """
    if os.path.exists(dirname):
        try:
            rmtree(dirname, ignore_errors=True)
            return False
        except OSError as e:
            err_log.warning(e)
            return True
    else:
        return False


def clone(uri: str, target: str, token: str) -> None:
    """Clone a private repo with access token

    uri: Repository uri less "https://"
    target: local directory name target; what will you call local?
    token: Github access token string

    example uri "github.com/DralrinResthal/ScanSlated-Portal.git"

    """
    remote = f"https://{token}:x-oauth-basic@{uri}"
    try:
        git.Repo.clone_from(remote, target)
        git_log.info(f"Repository '{uri}' has been cloned to {target}")

    except:
        msg = f"Unable to clone repository {uri}. {traceback.format_exc()}"
        err_log.warning(msg)


def reset_to_main(repo: str):
    """Switches repo to main branch

    repo: String name of local repo
    """
    repo = git.Repo(repo)
    try:
        repo.heads.main.checkout()
    except:
        err_log.warning("Placeholder, update this later")


def new_branch(repo: str) -> None:
    """Creates and switches to a new branch

    repo: Local repo name
    branch: Name of new branch
    """
    chars = string.ascii_letters + string.digits
    length = 20
    repo = git.Repo(repo)
    new_branch_name = "".join(random.choice(chars) for i in range(length))
    try:
        new_branch = repo.create_head(new_branch_name)
    except:
        return sys.exc_info()

    new_branch.checkout()

    return new_branch_name


def add_commit(
    repo: str, changes: list, message: str, name: str, email: str
) -> None:
    """Stage all changes and commit them in one single step.

    repo: local name of repository
    changes: List of all filenames to stage
    message: Commit message string
    name: Author name string
    email: Author email string
    """
    # Initialize repository
    repo = git.Repo(repo)
    # Stage chagnes
    repo.index.add(changes)
    author = Actor(name, email)
    committer = Actor("Config Manager", "configmgmt@example.com")
    # Commit staged changes
    repo.index.commit(message, author=author, committer=committer)
    # Push to remote
    repo.git.push("--set-upstream", repo.remote("origin"), repo.head.ref)


def pull(repo: str) -> None:
    """Pull (update) git repo

    repo: local name of repository
    """
    repo = git.Repo(repo)
    origin = repo.remotes.origin
    origin.pull()


def create_pr(
    lrepo: str,
    dir: str,
    token: str,
    title: str,
    body: str,
    head: str,
    base: str,
) -> None:
    """Create a new pull request

    repo: Repository in User/Repository format
    dir: local directory name
    token: Github access token
    title: Title of new pull request
    body: Body of pull request
    head: Branch to merge (dev -> main, this is dev)
    base: Branch to merge new branch into (dev -> main, this is main)
    """
    os.chdir(dir)
    g = Github(token)
    repo = g.get_repo(lrepo)
    repo.create_pull(title=title, body=body, head=head, base=base)
    os.chdir("../")
