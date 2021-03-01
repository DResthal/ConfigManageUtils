import boto3
from dotenv import load_dotenv
import os
import base64

load_dotenv()

# Data as read from a txt file
# data = bytes(open('raw.txt', 'r').read().encode(encoding="ascii"))


def encrypt(data: str) -> str:
    """Encrypts string data with AWS KMS
    Accepts a bytes string

    data: Bytes string to encrypt

    Returns base64 encoded string
    decode to ascii
    """
    kms = boto3.client("kms")
    res = kms.encrypt(
        KeyId=os.getenv("KEY_ID"),
        Plaintext=data,
        EncryptionAlgorithm="SYMMETRIC_DEFAULT",
    )

    return base64.b64encode(res["CiphertextBlob"])


def decrypt(data: str) -> str:
    """Decrypts string data using AWS KMS
    Accepts a bytes string

    data: Bytes string to decrypt

    Returns base64 encoded string
    decode to ascii
    """
    kms = boto3.client("kms")
    res = kms.decrypt(
        CiphertextBlob=data,
        KeyId=os.getenv("KEY_ID"),
        EncryptionAlgorithm="SYMMETRIC_DEFAULT",
    )

    return base64.b64encode(res["Plaintext"])
