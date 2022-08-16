# -*- coding: utf-8 -*-
import base64
import json
import logging
from typing import Any, Dict

import core_aws.kms
import core_aws.secret_manager
import jwt
from core_api.utils import get_header
from core_mts.connector import (
    MTS_API_KEY,
    MTS_ENDPOINT,
    get_host,
)
from core_utils.custom_requests import (
    AbstractRequest,
)
from core_utils.environment import (
    ENVIRONMENT,
)
from core_utils.utils import get_logger
from requests import request

__all__ = [
    "call_request",
    "TokenRefreshRequest",
    "RefreshTokenParameterException"
]

LOGGER = get_logger("core_mts.provider")


def get_decode_token(headers):
    """Decode JWT Token

    :param headers
    :return json decode token
    """
    token = headers["Authorization"]
    mts_token = jwt.decode(token, options={"verify_signature": False})["mtsToken"]
    return json.loads(base64.b64decode(mts_token).decode())


def call_request(method, url, params=None, body=None, headers=None):
    """Call request to merchant API

    :param method (GET, POST, PUT, PATCH, DELETE)
    :param url str
    :param body dict
    :param params dict
    :param headers dict
    :return HttpResponse
    """

    logging.info(url)
    body_data = json.dumps(body) if body else None
    return request(method, url, params=params, data=body_data, headers=headers)


def get_decode_wallet(wallet):
    """Decode JWT Wallet (is for testing purposes)

    :param wallet encode
    :return tuple client_id, currency
    """

    metadata = jwt.decode(wallet, options={"verify_signature": False})
    client_id = metadata.get('client_id')
    currency = metadata.get('currency')

    return client_id, currency


def read_wallet_data(wallet):
    client_id_and_currency = core_aws.kms.decrypt_data(wallet)
    return json.loads(client_id_and_currency)


def get_message_response(response):
    """Get the error message from the response

    Args:
        response (dict): call request response

    Returns:
        str: message
    """
    error = json.loads(response.text)
    message = error.get("errorDescription", None) or error.get("error_description", None)

    if not message:
        message = error["message"]

    return message


def login_admin(country, mts_api_key):
    """Login to MTS admin

    Args:
        country (str): country
        mts_api_key (str): identifier that serves as the means of authentication of a user

    Raises:
        ValueError: error generated not controlled

    Returns:
        tuple:  status_code, message, admin_authorization
    """
    try:
        mts_host = get_host(ENVIRONMENT, country, False)

        secret_credentials = core_aws.secret_manager.get_secret(f"{ENVIRONMENT.lower()}-{country}-device-administrative")
        body = json.loads(secret_credentials)

        url = f"{mts_host}/login"

        headers = {
            "x-api-key": mts_api_key
        }
        body.update(
            {"device_type": "ADMINISTRATIVE_DEVICE"}
        )

        response = call_request(method="POST", url=url, body=body, headers=headers)

        message = "success"
        status_code = response.status_code

        if status_code != 200:
            message = get_message_response(response)
            return status_code, message, None

        return status_code, message, response.json()["IdToken"]
    except Exception as e:
        LOGGER.error(e)
        raise ValueError(e)


class TokenRefreshRequest(AbstractRequest):
    def __init__(self, event: Dict[str, Any]):
        self.event = event

    def get_headers(self) -> dict:
        self.event["headers"].pop("Host", "")
        header_parameters = get_header(self.event)
        refresh_token = header_parameters.get("refresh-token")
        if not refresh_token:
            raise RefreshTokenParameterException()
        header_parameters.update({"x-api-key": self.event[MTS_API_KEY], "Content-Type": "application/json"})
        return header_parameters

    def get_method(self) -> str:
        return "GET"

    def get_url(self) -> str:
        return self.event[MTS_ENDPOINT]

    def get_params(self):
        return None

    def get_body(self):
        return None


class RefreshTokenParameterException(Exception):
    def __init__(self):
        super().__init__(self, "Missing refresh-token parameter")
