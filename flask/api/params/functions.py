import boto3
import base64
from flask import current_app
from logging import getLogger
import sys


err_log = getLogger("elog")


def get_credentials(env: str = None):
    """
    Get the Assumed Role credentials of the role being assumed, setup in config.py

    Parameters
    ----------
    env: str: The environment variable of the AWS credentials

    Response
    --------
    Returns a dictionary containing the assumed role's AWS credentials
    """
    try:
        sts_client = boto3.client("sts")
    except:
        err_log.warning("Unable to create sts client.")
        err_log.warning(sys.exc_info())
        return "Error creating sts client, see logs for more details", 500

    if env.lower() == "dev":
        role_arn = current_app.config["DEV_ARN"]
        role_session_name = "DevSession"
        kms_key = current_app.config["DEV_KMS_KEY"]

    if env.lower() == "prod":
        role_arn = current_app.config["PRD_ARN"]
        role_session_name = "ProdSession"
        kms_key = current_app.config["PRD_KMS_KEY"]

    try:
        assumed_role = sts_client.assume_role(
            RoleArn=role_arn, RoleSessionName=role_session_name
        )
    except:
        err_log.warning(
            "Unable to assume role and receive role object containing credentials"
        )
        err_log.warning(sys.exc_info())
        return "Unalbe to assume role. See logs for more details", 500

    try:
        credentials = assumed_role["Credentials"]
    except KeyError:
        err_log.warning(
            "assumed_role does not contain key Credentials, something else has gone horribly wrong."
        )
        err_log.warning(sys.exc_info())
        return (
            "Unable to extract credentials from the assumed_role object. See logs for more details",
            500,
        )

    return credentials, kms_key


def redacted(data: list) -> list:
    """
    Replace the key "value" of a dictionary object with "REDACTED", if the dictionary contains a "secret":"True" key:value pair

    Parameters
    ----------
    data: List of dictionaries to check and update

    Response
    --------
    List of dictionaries as provided with the replaced value "REDACTED"
    """
    for i in data:
        if i["secret"]:
            i["value"] = "REDACTED"

    return data


def prefix_names(data: list) -> list:
    """
    Combine the prefix and the name of a each dictionary in a list

    Parameters
    ----------
    """
    for param in data:
        param["name"] = "/" + param["prefix"] + "/" + param["name"]
    return data


def enc(data: str, env: str = None) -> str:
    """
    Encrypts the given string data with AWS KMS

    Parameters
    ----------
    data: String to encrypt
    env: Which AWS role to assume

    Response
    --------
    Encrypted string
    """
    credentials, kms_key = get_credentials(env.lower())

    try:
        kms = boto3.client(
            "kms",
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
        )
    except:
        err_log.warning("Unable to create client 'kms'")
        err_log.warning(sys.exc_info())
        return "Unable to create KMS client. See logs for more details", 500

    try:
        res = kms.encrypt(
            KeyId=kms_key,
            Plaintext=data,
            EncryptionAlgorithm="SYMMETRIC_DEFAULT",
        )
        enc_data = base64.b64encode(res["CiphertextBlob"])
        enc_data = enc_data.decode("ascii")
        return enc_data
    except:
        err_log.warning(f"Error in enc(). \n {sys.exc_info()}")
        return "An encrypted error occurred, refer to logs."


def dec(data: str, env: str = None) -> str:
    """
    Decrypts an encrypted string with AWS KMS

    Parameters
    ----------
    data: The encrypted string to decrypt
    env: Which AWS role to assume

    Response
    --------
    Decrypted string
    """
    try:
        data = base64.b64decode(data)
    except:
        raise

    credentials, kms_key = get_credentials(env.lower())

    try:
        kms = boto3.client(
            "kms",
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
        )
    except:
        err_log.warning("Unable to create client 'kms'")
        err_log.warning(sys.exc_info())
        return "Unable to create KMS client. See logs for more details", 500

    res = kms.decrypt(CiphertextBlob=data, KeyId=kms_key)
    dec_bytes = res["Plaintext"]
    return dec_bytes.decode("ascii")


def store_ps(data: list, env: str = None) -> list:
    """
    Stores data in AWS Parameter store under SSM

    Parameters
    ----------
    data: List of dictionaries representing parameters to store
    env: Which AWS role to assume

    Response
    --------
    List of AWS SSM responses as dictionaries for each parameter stores.
    """
    credentials, _ = get_credentials(env.lower())

    try:
        ssm = boto3.client(
            "ssm",
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
        )
    except:
        err_log.warning("Unable to create client 'ssm'")
        err_log.warning(sys.exc_info())
        return "Unable to create SSM client. See logs for more details", 500

    response_list = []

    for param in data:
        try:
            param.pop("prefix")
            if param["secret"]:
                param["value"] = dec(param["value"], env)
                res = ssm.put_parameter(
                    Name=param["name"],
                    Value=param["value"],
                    Description=param["comment"],
                    Type="SecureString",
                    KeyId=current_app.config["KMS_KEY_ID"],
                    Overwrite=True,
                )
                response_list.append(res)
            else:
                res = ssm.put_parameter(
                    Name=param["name"],
                    Value=param["value"],
                    Description=param["comment"],
                    Type="String",
                    Overwrite=True,
                )
                response_list.append(res)
        except:
            err_log.warning(sys.exc_info())
            response_list.append(f"Error in {param['name']}")

    return response_list
