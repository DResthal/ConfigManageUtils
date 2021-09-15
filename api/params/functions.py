import boto3
import base64
from flask import current_app


def enc(data: str) -> str:
    data = bytes(data.encode("ascii"))
    bsess = boto3.Session(profile_name="default")
    kms = bsess.client("kms")
    res = kms.encrypt(
        KeyId=current_app.config["KMS_KEY_ID"],
        Plaintext=data,
        EncryptionAlgorithm="SYMMETRIC_DEFAULT",
    )

    return base64.b64encode(res["CiphertextBlob"]).decode("ascii")
