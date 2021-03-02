import json
import ruamel.yaml
import sys
from distutils.util import strtobool
from . import aws

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
        json_string = json.dumps(content)
        return json_string
    except TypeError as e:
        return e
    except:
        return(f"Unknown Error parsing {filename} to json. {sys.exc_info()}")

# Check for secret flag.
# Encrypt/Decrypt secret value per decrypt flag.
# Return entire dict.
def check_secret(data: str, decrypt: bool=False) -> str:
    """Checks for secret flag, encrypts value if secret True

    data: JSON String to check
    decrypt: Boolean flag to decrypt instead of encrypting
    Returns JSON String
    """
    try:
        data = json.loads(data)
    except json.decoder.JSONDecodeError as e:
        return f"Invalid JSON: {e}"

    # Check for secret flag, encrypt/decrypt as necessary
    for key in data.keys():
        for k, v in data[key].items():
            if k == "secret" and v == True:
                data = data
                '''
                if decrypt:
                    data[key]['value'] = aws.decrypt(data[key]['value'])
                else:
                    data[key]["value"] = aws.encrypt(
                        data[key]['value']
                        )
                '''

    data = json.dumps(data)

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
