import boto3
from dotenv import load_dotenv
import os
import base64
import json
from . import file

load_dotenv()

# Data as read from a txt file
# data = bytes(open('raw.txt', 'r').read().encode(encoding="ascii"))


def encrypt(data: str) -> str:
    """Encrypts string data with AWS KMS

    data: String to encrypt

    Returns base64 encoded string
    """
    data = bytes(data.encode("ascii"))
    kms = boto3.client("kms")
    res = kms.encrypt(
        KeyId=os.getenv("KEY_ID"),
        Plaintext=data,
        EncryptionAlgorithm="SYMMETRIC_DEFAULT",
    )

    return base64.b64encode(res["CiphertextBlob"]).decode("ascii")


def decrypt(data: str) -> str:
    """Decrypts string data using AWS KMS

    data: String to encrypt
    Returns base64 encoded string
    """
    data = base64.b64decode(data)
    kms = boto3.client("kms")
    res = kms.decrypt(
        CiphertextBlob=data,
        KeyId=os.getenv("KEY_ID"),
        EncryptionAlgorithm="SYMMETRIC_DEFAULT",
    )

    return res["Plaintext"].decode("ascii")


def store(data: str) -> dict:
    """Stores JSON string key:values in parameter store

    data: JSON String of data to store

    Returns AWS SSM response as dict
    """

    data = json.loads(file.check_secret(data, decrypt=True))
    ssm = boto3.client("ssm")
    for key in data.keys():
        if data[key]["secret"]:
            res = ssm.put_parameter(
                Name=key,
                Description=data[key]["comment"],
                Value=data[key]["value"],
                Type="SecureString",
                KeyId=os.getenv("KEY_ID"),
                Overwrite=True,
            )
        else:
            res = ssm.put_parameter(
                Name=key,
                Description=data[key]["comment"],
                Value=data[key]["value"],
                Type="String",
                Overwrite=True,
            )
        yield (res)
