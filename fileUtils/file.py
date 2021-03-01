import json
import ruamel.yaml
import sys
from distutils.util import strtobool
import aws

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
            except raumel.yaml.YAMLError as e:
                e_msg = f"Error loading yaml file. \n\n{e}"
                return e_msg
    except FileNotFoundError as e:
        return f"File Not Found: {e}"
    except:
        return f"{sys.exc_info()}"

    try:
        unencrypted_content = check_secret(content, decrypt=True)
        json_string = json.dumps(unencrypted_content)
        return json_string
    except TypeError as e:
        return e
    except:
        return(f"Unknown Error parsing {filename} to json. {sys.exc_info()}")


# Pre-process incoming JSON.
# Send through encryption check.
# Return encrypted JSON dict for writing to yml file.
def process_json(payload: str) -> str:
    """Convert JSON payload to ruamel.yaml object
    If JSON contains 'secret':True then encrypt relevant value

    payload: JSON string to convert
    """
    try:
        payload = json.loads(
            payload, object_pairs_hook=ruamel.yaml.comments.CommentedMap
        )
    except TypeError as e:
        return f"Error parsing JSON \n\n{e}"
    except:
        return f"Unknown error parsing JSON. {sys.exc_info()}"

    encrypted_data = check_secret(payload)

    return encrypted_data


# Check for secret flag.
# Encrypt/Decrypt secret value per decrypt flag.
# Return entire dict.
def check_secret(data: dict, decrypt: bool=False) -> dict:
    """Walks dict tree and checks for key "secret"
    If secret : True, returns dict, pass if False

    data: Python dictionary object
    """
    for key in data.keys():
        for k, v in data[key].items():
            if k == "secret" and v == True:
                if decrypt:
                    data[key]['value'] = aws.decrypt(data[key]['value'])
                else:
                    data[key]["value"] = aws.encrypt(
                        data[key]['value']
                        )
    return data


# Convert JSON to yaml and write to file.
# Conversion cannot be done outside of this as ruamel.yaml's dump
# function requires a stream to convert to yaml, and that stream
# is the outfile.
def write_file(filename: str, payload: str) -> None:
    yaml = ruamel.yaml.YAML()
    yaml.explicit_start = True
    write_file = open(filename, "w")
    try:
        yaml.dump(payload, write_file)
    except:
        return f"Error saving yaml file. {sys.exc_info()}"
