from dotenv import load_dotenv
from github import Github
import git
import sys
import os

load_dotenv()

token = os.getenv("ACCESS_TOKEN")


def clone(uri: str, target: str, token: str) -> None:
    """Clone a private repo with access token

    uri: Repository uri less "https://"
    target: local directory name target; what will you call local?
    token: Github access token string

    example uri "github.com/DralrinResthal/ScanSlated-Portal.git"

    """
    remote = f"https://{token}:x-oauth-basic@{uri}.git"
    try:
        git.Repo.clone_from(remote, target)
    except:
        return sys.exc_info()


def new_branch(repo: str, branch: str) -> None:
    """Creates and switches to a new branch

    repo: Local repo name
    branch: Name of new branch
    """
    repo = git.Repo(repo)
    try:
        new_branch = repo.create_head(branch)
    except:
        return ()
    new_branch.checkout()


def add_commit(repo: str, changes: list, message: str) -> None:
    """Stage all changes and commit them in one single step.

    repo: local name of repository
    changes: List of all filenames to stage
    message: Commit message string
    """
    # Initialize repository
    repo = git.Repo(repo)
    # Stage chagnes
    repo.index.add(changes)
    # Commit staged changes
    repo.index.commit(message)
    # Push to remote
    repo.git.push("--set-upstream", repo.remote("origin"), repo.head.ref)


def create_pr(
    repo: str, dir: str, token: str, title: str, body: str, head: str, base: str
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
    repo = g.get_repo(repo)
    repo.create_pull(title=title, body=body, head=head, base=base)
    os.chdir("../")