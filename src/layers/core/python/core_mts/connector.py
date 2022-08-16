# -*- coding: utf-8 -*-
import base64
import datetime
import json
import os
from functools import partial, wraps
from typing import Any, Callable, Dict

import core_aws.secret_manager
import core_aws.ssm
import jwt as jwt
import requests
from core_api.responses import (
    api_response,
)
from core_api.utils import get_header
from core_utils.utils import get_logger

COUNTRY = "country"
AUTHORIZATION = "Authorization"
DEVICE_ID = "DEVICE_ID"

MTS_HOST = "mtsHost"
MTS_ENDPOINT = "mtsEndpoint"
MTS_API_KEY = "mtsApiKey"
MTS_TOKEN = "mtsToken"

LOGGER = get_logger("core_mts.connector")


def decode_token(token):
    return jwt.decode(token, options={"verify_signature": False})


def request_client_id(*, mts_token, host, mts_api_key):
    try:
        token_data = decode_token(mts_token)
        _mts_token = token_data.get(MTS_TOKEN)
        device_key = json.loads(base64.b64decode(_mts_token).decode())["DEVICE_KEY"]

        url = f"{host}/accounts/msisdn/{device_key}"
        headers = {
            "Authorization": mts_token,
            "x-api-key": mts_api_key,
            "Date": str(datetime.datetime.now().date()),
        }

        response = requests.get(url, headers=headers)

        return next(filter(lambda x: x["key"] == "CLIENT_ID", response.json()["metadata"]))["value"]
    except Exception as e:
        LOGGER.error(e)
        raise ValueError(e)


def get_country(header_parameters, environment):
    try:
        return header_parameters.get("Host", "").split(".")[2 if environment != "prod" else 1].lower()
    except Exception as e:
        LOGGER.error(e)
        return ""


def get_host(environment, country, use_mts_version):
    try:
        host_data = core_aws.ssm.get_parameter(f"/{environment.lower()}/{country.lower()}/api/connector/host")

        return f"https://{host_data.get('host')}{host_data.get('version') if use_mts_version else ''}"
    except Exception as e:
        LOGGER.error(e)
        raise ValueError(e)


def get_api_key(environment, country):
    try:
        return core_aws.secret_manager.get_secret(f"{environment.lower()}-{country.lower()}-api-connector-api-key")
    except Exception as e:
        LOGGER.error(e)
        raise ValueError(e)


def interceptor(function: Callable[[Dict, Any], Any] = None, use_token_to_get_metadata: bool = True, mts_path: str = None, get_client_id: bool = False, use_mts_version: bool = True):
    """Inject host, apikey to mts request"""

    if function is None:
        return partial(interceptor, use_token_to_get_metadata=use_token_to_get_metadata, mts_path=mts_path, get_client_id=get_client_id, use_mts_version=use_mts_version)

    @wraps(function)
    def decorator(event, context):
        environment = os.getenv("ENVIRONMENT")
        header_parameters = get_header(event)

        authorization = header_parameters.get(AUTHORIZATION)
        country = get_country(header_parameters, environment)

        if use_token_to_get_metadata and authorization:
            token_data = decode_token(authorization)
            country = token_data.get(COUNTRY, "").lower()

            metadata = {
                COUNTRY: country,
            }

            mts_token = token_data.get(MTS_TOKEN)

            if mts_token:
                metadata.update(json.loads(base64.b64decode(mts_token).decode()))

            event.update(metadata)

        api_key = get_api_key(environment, country)
        mts_host = get_host(environment, country, use_mts_version)

        if get_client_id and authorization:
            try:
                client_id = request_client_id(mts_token=authorization, host=mts_host, mts_api_key=api_key)
                event.update(
                    {
                        "client_id": client_id
                    }
                )
            except Exception:
                return api_response("Invalid token", 400)

        mts_endpoint = mts_host + (mts_path or "")
        event.update(
            {
                MTS_HOST: mts_host,
                MTS_ENDPOINT: mts_endpoint,
                MTS_API_KEY: api_key
            }
        )

        return function(event, context)

    return decorator
