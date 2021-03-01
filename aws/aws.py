import boto3
from dotenv import load_dotenv
import os
import base64

load_dotenv()

# Data as read from a txt file
# data = bytes(open('raw.txt', 'r').read().encode(encoding="ascii"))

def encrypt(data):
    kms = boto3.client('kms')
    res = kms.encrypt(
        KeyId=os.getenv('KEY_ID'),
        Plaintext=data,
        EncryptionAlgorithm="SYMMETRIC_DEFAULT"
    )

    return(base64.b64encode(res['CiphertextBlob']))

def write_out(res):
    with open('encrypted.txt', 'w') as f:
        f.write(res.decode('ascii'))
        f.close()
    print('Written to file.')
