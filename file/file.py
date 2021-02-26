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
        message = f"Unknown Error parsing {filename} to json. {sys.exc_info()}"
        return message


def convert_json(payload: str, filename: str) -> None:
    '''Convert JSON payload to yaml and write to filename

    payload: JSON String to convert
    filename: Filename to write yaml to
    '''
    yaml = ruamel.yaml.YAML()
    try:
        jsn = json.loads(payload, object_pairs_hook=ruamel.yaml.comments.CommentedMap)
    except TypeError as e:
        return(f'Error parsing JSON \n\n{e}')
    except:
        return(f"Unknown error parsing JSON. {sys.exc_info()}")

    yaml.explicit_start = True
    write_file = open(filename, 'w')
    try:
        yaml.dump(jsn, write_file)
    except:
        return(f"Error saving yaml file. {sys.exc_info()}")


def save_newfile():
    # Save new yaml to file
    pass


def check_secret():
    # Check if new config is set to secret
    pass
