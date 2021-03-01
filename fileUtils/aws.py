import boto3
from dotenv import load_dotenv
import os
import base64

load_dotenv()

# Data as read from a txt file
# data = bytes(open('raw.txt', 'r').read().encode(encoding="ascii"))


def encrypt(data: str) -> str:
    """Encrypts data with AWS KMS
    Accepts a bytes string from ascii

    data: Bytes string to encrypt
    """
    kms = boto3.client("kms")
    res = kms.encrypt(
        KeyId=os.getenv("KEY_ID"),
        Plaintext=data,
        EncryptionAlgorithm="SYMMETRIC_DEFAULT",
    )

    return base64.b64encode(res["CiphertextBlob"])


def decrypt(data: str) -> str:
    """Decrypts string using AWS KMS"""
    kms = boto3.client("kms")
    res = kms.decrypt(
        CiphertextBlob=data,
        KeyId=os.getenv("KEY_ID"),
        EncryptionAlgorithm="SYMMETRIC_DEFAULT",
    )

    return base64.b64encode(res["Plaintext"])


def write_out(data: str):
    with open("encrypted.txt", "w") as f:
        f.write(data.decode("ascii"))
        f.close()
    print("Written to file.")
