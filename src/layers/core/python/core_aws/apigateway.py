# -*- coding: utf-8 -*-
import logging

import boto3
from botocore.exceptions import (
    ClientError,
)

__all__ = [
    "get_apikey_by_tag",
]

apigateway = boto3.client("apigateway")


def get_apikey_by_tag(*, key="Integrator:ApiKey", value="MerchantSetup"):
    """Gets apikey by resource key tag

    Args:
        key (str, optional): The key name of the tag. Defaults to "Integrator:ApiKey"
        value (str, optional): The value for the tag. Defaults to "MerchantSetup".

    Returns:
        str:   api_key
    """
    try:
        response = apigateway.get_api_keys(includeValues=True)
        api_key = None

        for items in response["items"]:
            if "tags" in items:
                for tag in items["tags"]:
                    if key == tag and value == items["tags"][tag]:
                        api_key = items["value"]
                        break
            if api_key:
                break

    except ClientError as e:
        logging.error(e)
        return None

    logging.debug(api_key)

    if not api_key:
        return None

    return api_key
