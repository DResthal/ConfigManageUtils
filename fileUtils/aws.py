import boto3
from dotenv import load_dotenv
import os
import base64

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

    return base64.b64encode(res["CiphertextBlob"])


def decrypt(data: str) -> str:
    """Decrypts string data using AWS KMS

    data: String to encrypt

    Returns base64 encoded string
    """
    data = bytes(data.encode("ascii"))
    kms = boto3.client("kms")
    res = kms.decrypt(
        CiphertextBlob=data,
        KeyId=os.getenv("KEY_ID"),
        EncryptionAlgorithm="SYMMETRIC_DEFAULT",
    )

    return base64.b64encode(res["Plaintext"])


def store(data: str) -> None:
    """Stores JSON string key:values in parameter store

    data: JSON String of data to store
    """
    ssm = boto3.client("ssm")
    for key in data.keys():

        res = ssm.put_parameter(
            Name=key,
            Description=data[key]["comment"],
            Value=data[key]["comment"],
            Type="SecureString",
            KeyId=os.getenv("KEY_ID"),
            Overwrite=True,
        )
        print(res)
