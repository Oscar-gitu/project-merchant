# -*- coding: utf-8 -*-
import base64
import json
import urllib

import boto3
from core_aws.ssm import get_parameter


def get_kms_client():
    return boto3.client("kms")


def encrypt_data(data, kms_parameter_name):
    client = get_kms_client()
    key_arn_kms = get_parameter(kms_parameter_name, is_dict=False)
    encrypted_data = client.encrypt(KeyId=key_arn_kms,
                                    Plaintext=json.dumps(data))
    return base64.b64encode(encrypted_data["CiphertextBlob"]).decode()


def decrypt_data(data):
    data = urllib.parse.unquote(data)
    client = get_kms_client()
    response = client.decrypt(
        CiphertextBlob=base64.b64decode(data)
    )
    return response["Plaintext"].decode()
