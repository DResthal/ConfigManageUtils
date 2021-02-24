import git
from sys import exc_info
from logger import CustomLogger

e_log = CustomLogger('e_log', 'error.log', level=logging.DEBUG).create_logger()


def clone(uri: str, name: str) -> None:
    """Clone a git repo

    uri: String: Github repository uri
    name: String: Repository name to clone to
    """
    try:
        git.Repo.clone_from(uri, name)
    except:
        e_log.warning(exc_info())


def commit(repo: str, files: list, message: str) -> None:
    """Add and commit changes to the repository

    repo: String name of the repository, local name
    files: List: List of files to commit
    message: String: Commit message string
    """
    repo = git.Repo(repo)
    try:
        repo.index.add(files)
        return "Staged changes"
    except CacheError as e:
        e_log.warning(e)
    except:
        e_log.warning(exc_info())

    try:
        repo.index.commit(message)
        return "Commit Successful"
    except CacheError as e:
        e_log.warning(e)
    except:
        e_log.warning(exc_info())


def read_file(filename: str, change: str) -> None:
    """Rewrite entire file with new contents

    change: String: String formatted file contents
    At this time, please include the entire new contents
    of the file, including non-changed text
    """
    try:
        with open(filename, "w") as f:
            f.write(change)
            f.close()
    except:
        e_log.warning(exc_info())


def new_branch(repo: str, name: str) -> None:
    '''Create a new branch and immediately checkout

    repo: String name of repository (local name)
    name: String name of new branch
    '''
    try:
        repo = git.Repo(repo)
    except:
        e_log.warning(exc_info())
    try:
        repo.git.branch(name)
        repo.git.checkout(name)
        print(f"New branch {name} created and checked out")
    except GitError as e:
        e_log.warning(e)
    except:
        e_log.warning(exc_info())
