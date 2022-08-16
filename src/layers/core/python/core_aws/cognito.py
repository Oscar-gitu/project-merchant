# -*- coding: utf-8 -*-
import os

import boto3
from botocore.exceptions import (
    ClientError,
)
from core_aws.ssm import get_parameter


def get_cognito_headers(*, region, client_id, username, password, user_pool_id, domain):
    """
    Get the headers for the request to cognito.

    Parameters
    ----------
    region : str
        Region where the cognito instance is located.
    client_id : str
        Client id of the cognito instance client.
    username : str
        Username for login.
    password : str
        Password for login.
    user_pool_id : str
        User pool id of the cognito instance.
    domain : str
        Domain where the cognito instance is located.

    Returns
    -------
    dict
        Headers for the request to cognito.

    Examples
    --------
    >>> from core_aws.cognito import get_cognito_headers
    >>> get_cognito_headers('us-east-1', 'client_id', 'username', 'password', 'user_pool_id', 'domain')

    """
    client = boto3.client(
        "cognito-idp",
        aws_access_key_id="",
        aws_secret_access_key="",
        region_name=region,
    )
    response = client.initiate_auth(
        ClientId=client_id,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": password},
        ClientMetadata={"UserPoolId": user_pool_id},
    )

    headers = {
        "Authorization": f"Bearer {response.get('AuthenticationResult').get('IdToken')}",
        "content-type": "application/json",
    }
    return headers, domain


def get_token_cognito(
    *,
    client_id,
    username,
    password,
    user_pool_id,
    region_name="us-east-1",
    auth_flow="USER_PASSWORD_AUTH",
    bearer=True,
):
    """
    Get the token for the request to cognito.

    Parameters
    ----------
    client_id : str
        Client id of the cognito instance client.
    username : str
        Username for login.
    password : str
        Password for login.
    user_pool_id : str
        User pool id of the cognito instance.
    region_name : str
        Region where the cognito instance is located.
        us-east-1 by default.
    auth_flow : str
        Authentication flow.
        USER_PASSWORD_AUTH by default.
    bearer : bool
        If True, return the token as a bearer token.
        True by default.

    Returns
    -------
    str
        Token for the request to cognito.
        Bearer TOKEN if bearer param is true
        TOKEN if the bearer param is false

    Examples
    --------
    >>> from core_aws.cognito import get_token_cognito
    >>> get_token_cognito('client_id', 'username', 'password', 'user_pool_id')

    """
    client = boto3.client("cognito-idp", region_name=region_name)
    response = client.initiate_auth(
        ClientId=client_id,
        AuthFlow=auth_flow,
        AuthParameters={"USERNAME": username, "PASSWORD": password},
        ClientMetadata={"UserPoolId": user_pool_id},
    )
    token = response.get("AuthenticationResult", {}).get("IdToken")
    if bearer:
        return f"Bearer {token}"
    else:
        return token


def create_new_user(*, email, parent, region="us-east-1"):
    client = boto3.client("cognito-idp", region)
    parameter_name_pool_id = f'MERCHANT_POOL_ID_{os.getenv("ENVIRONMENT")}'
    try:
        response = client.admin_create_user(
            UserPoolId=os.getenv(parameter_name_pool_id)
            or get_parameter(parameter_name_pool_id, is_dict=False),
            Username=email,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "custom:parent", "Value": parent},
            ],
            ValidationData=[{"Name": "email", "Value": email}],
        )
    except ClientError as e:
        if "UsernameExistsException" in str(e):
            raise UsernameExistsException(str(e))
        else:
            raise e
    return response


class UsernameExistsException(Exception):
    def __init__(self, message):
        super().__init__(message)
