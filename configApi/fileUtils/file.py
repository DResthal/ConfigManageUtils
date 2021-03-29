import json
import ruamel.yaml
import sys
from . import aws
from datetime import datetime


# Read's yaml file.
# Decrypts yml
# Returns JSON str
def read_yaml(filename: str) -> str:
    """Reads yaml file which is converted to
    json by ruamel.yaml natively.

    filename: Filename to convert
    """
    yaml = ruamel.yaml.YAML(typ="safe")
    try:
        with open(filename, "r") as f:
            data = f.read()
            try:
                content = yaml.load(data)
            except ruamel.yaml.YAMLError as e:
                e_msg = f"Error loading yaml file. \n\n{e}"
                return e_msg
    except FileNotFoundError as e:
        return f"File Not Found: {e}"
    except:
        return f"{sys.exc_info()}"

    try:
        json_string = json.dumps(content)
        return json_string
    except TypeError as e:
        return e
    except:
        return f"Unknown Error parsing {filename} to json. {sys.exc_info()}"


# Check for secret flag.
# Encrypt/Decrypt secret value per decrypt flag.
# Return entire dict.
def check_secret(
    data: str, decrypt: bool = False, delete: bool = False
) -> str:
    """Checks for secret flag, encrypts value if secret True

    data: JSON String to check
    decrypt: Boolean flag to decrypt instead of encrypting
    delete: Boolean flag to include removal of values containing "delete" : true

    Returns JSON String

    Notes: The delete flag is necessary to avoid checking for "delete" on JSON that
    is not intended to be modified such as that sent to AWS SSM.
    """
    try:
        data = json.loads(data)
    except json.decoder.JSONDecodeError as e:
        return f"Invalid JSON: {e}"

    if delete:
        for key in data.copy().keys():
            for k, v in data[key].items():
                if k == "delete" and v:
                    del data[key]

    # Check for secret flag, encrypt/decrypt as necessary
    for key in data.keys():
        for k, v in data[key].items():
            if k == "secret" and v:
                data = data
                if decrypt:
                    data[key]["value"] = aws.decrypt(data[key]["value"])
                else:
                    data[key]["value"] = aws.encrypt(data[key]["value"])

    data = json.dumps(data)
    return data


def last_modified(data: dict) -> dict:
    """Add "last_modified" date and user for each updated parameter

    data: The entire params dict from request.json
    """

    user = data["userInfo"]["username"]
    date = datetime.now().strftime("%m-%d-%Y %H:%M:%S")

    for key in data.keys():
        for k, v in data[key].items():
            v.update({"last_modified": {"date": date, "user": user}})

    return data


# Convert JSON to yaml and write to file.
# Conversion cannot be done outside of this as ruamel.yaml's dump
# function requires a stream to convert to yaml, and that stream
# is the outfile.
def write_file(data: str, filename: str) -> None:
    """Saves a JSON string to a yml file.

    data: JSON String to save.
    filename: Name of file to save to.
    """
    try:
        data = json.loads(data)
    except json.decoder.JSONDecodeError as e:
        return f"Invalid JSON: {e}"

    yaml = ruamel.yaml.YAML()
    original = json.loads(read_yaml(filename))
    # Updates the original dict, not data
    # Does not "return" a value so cannot reassign to data
    original.update(data)

    write_file = open(filename, "w")
    try:
        # Because we want to write the newly updated "original" dict
        yaml.dump(original, write_file)
    except:
        return f"Error saving yaml file. {sys.exc_info()}"
