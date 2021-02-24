from dotenv import load_dotenv
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

    example uri "github.com/DralrinResthal/ScanSlated-Portal"

    """
    remote = f"https://{token}:x-oauth-basic@{owner}/{repo}.git"
    try:
        git.Repo.clone_from(remote, target)
    except GitError as e:
        return e
    except:
        return sys.exc_info()


def new_branch(repo: str, branch: str) -> None:
    '''Creates and switches to a new branch

    repo: Local repo name
    branch: Name of new branch
    '''
    repo = git.Repo(local_repo)
    try:
        new_branch = repo.create_head(branch_name)
    except:
        return()
    new_branch.checkout()


def update_file(filename: str, content: str) -> None:
    '''Overwrite the entire file contents with new content
    Please provide the ENTIRE file contents each time this
    function is called

    filename: Name of file to chagne, preffered full path if possible
    content: New contents of the file in string format
    '''
    with open(filename, 'w') as f:
        f.write(content)
        f.close()

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
    repo.git.push('--set-upstream', repo.remote('origin'), repo.head.ref)

    