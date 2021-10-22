import boto3
import base64
from flask import current_app
import sys


def get_client(env: str = None, client: str = None):
    """
    Creates a Boto3 resource as a replacement to a normal low-level client, using the assumed credentials of the provided environment parameter

    Parameters
    ----------
    env: Environment representing the ARN to use
    client: The Boto3 resource to create. i.e. kms

    Response
    --------
    Boto3 resource using the assumed credentials
    """
    try:
        sts_client = boto3.client("sts")
    except:
        raise

    if env.lower() == "dev":
        role_arn = current_app.config["DEV_ARN"]
        role_session_name = "DevSession"

    if env.lower() == "prod":
        role_arn = current_app.config["PRD_ARN"]
        role_session_name = "ProdSession"

    try:
        assumed_role = sts_client.assume_role(
            RoleArn=role_arn, RoleSessionName=role_session_name
        )
    except:
        raise

    try:
        credentials = assumed_role["Credentials"]
    except KeyError:
        raise

    try:
        resource = boto3.resource(
            client,
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
        )
    except:
        raise

    return resource


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
    try:
        kms = get_client(env, "kms")
        res = kms.encrypt(
            KeyId=current_app.config["KMS_KEY_ID"],
            Plaintext=data,
            EncryptionAlgorithm="SYMMETRIC_DEFAULT",
        )
        enc_data = base64.b64encode(res["CiphertextBlob"])
        enc_data = enc_data.decode("ascii")
        return enc_data
    except:
        return f"AWS/Boto3 error in enc() {sys.exc_info()}", 500


def dec(data: str) -> str:
    """
    Decrypts an encrypted string with AWS KMS

    Parameters
    ----------
    data: String to decrypt: Ensure this is an encrypted string and not a raw string or encoding will break.

    Response
    --------
    Decrypted string
    """
    try:
        data = base64.b64decode(data)
    except:
        raise

    kms = boto3.client("kms")
    res = kms.decrypt(
        CiphertextBlob=data, KeyId=current_app.config["KMS_KEY_ID"]
    )
    dec_bytes = res["Plaintext"]
    return dec_bytes.decode("ascii")


def store_ps(data: list) -> list:
    """
    Stores data in AWS Parameter store under SSM

    Parameters
    ----------
    data: List of dictionaries representing parameters to store

    Response
    --------
    List of AWS SSM responses as dictionaries for each parameter stores.
    """
    try:
        ssm = boto3.client("ssm")
    except:
        return "Unable to create client 'ssm'", 500

    response_list = []

    for param in data:
        try:
            param.pop("prefix")
            if param["secret"]:
                param["value"] = dec(param["value"])
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
            response_list.append(f"Error in {param['name']}")

    return response_list
