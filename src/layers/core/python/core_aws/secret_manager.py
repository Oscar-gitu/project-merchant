import boto3
from botocore.exceptions import ClientError

SECRET_CLIENT = boto3.client("secretsmanager")


def get_secret(secret_name):
    try:
        get_secret_value_response = SECRET_CLIENT.get_secret_value(
            SecretId=secret_name
        )
        secret = get_secret_value_response['SecretString']
    except (KeyError, ClientError) as e:
        print(f"Error: {e}")
        raise e
    else:
        return secret
