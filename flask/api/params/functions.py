import boto3
import base64
from flask import current_app


def enc(data: str) -> str:

    # KMS requires a bytes object, convert to ascii then bytes here
    data = bytes(data.encode("ascii"))
    kms = boto3.Session(profile_name="default").client("kms")
    res = kms.encrypt(
        KeyId=current_app.config["KMS_KEY_ID"],
        Plaintext=data,
        EncryptionAlgorithm="SYMMETRIC_DEFAULT",
    )

    # 09/15/2021
    # KMS returns an object with an attribute named CiphertextBlob, this needs to be encoded
    # Decode the response to ascii, then encode that response in Base64
    # I honestly don't remember why, but this is the only way it works.
    return base64.b64encode(res["CiphertextBlob"]).decode("ascii")


def dec(data: str) -> str:
    # data starts off as a base64 encoded string, decode this to feed into KMS
    # Again, I don't remember why b64 is necessary, but this is the only way it works.
    data = base64.b64decode(data)
    kms = boto3.Session(profile_name="default").client("kms")
    r = kms.decrypt(CiphertextBlob=data)

    # KMS decrypt returns a bytes string as Plaintext attribute
    # Decode this bytes string to ascii for python.
    return r["Plaintext"].decode("ascii")


def store(data: list) -> list:
    ssm = boto3.Session(
        profile_name="default", region_name="us-east-1"
    ).client("ssm")
    response_list = []

    for param in data:
        if param["secret"]:
            res = ssm.put_parameter(
                Name=param["name"],
                Value=dec(param["value"]),
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

    return response_list
