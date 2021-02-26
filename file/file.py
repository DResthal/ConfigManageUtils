import json
import ruamel.yaml
import sys


def read_yaml(filename: str) -> None:
    """Reads yaml file which is converted to
    json by ruamel.yaml natively.

    filename: String filename to convert
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
        content = json.dumps(content)
        return content
    except TypeError as e:
        return e
    except:
        message = f"Unknown Error parsing {filename} to json. \n\n {sys.exc_info()}"
        return message


def convert_json():
    # Convert JSON to yaml
    pass


def save_newfile():
    # Save new yaml to file
    pass


def check_secret():
    # Check if new config is set to secret
    pass
