# -*- coding: utf-8 -*-
import json

from core_utils.utils import (
    cast_default,
)

__all__ = ["api_response"]


def api_response(body, status_code):
    """
    Parse the lambda response and return a dict with the http response.
    Parameters
    ----------
    body : Any
        The body of the lambda response.
    status_code : int

    Returns
    -------
    dict
        The response to be returned to the client.

    Examples
    --------
    >>> from core_api.responses import api_response
    >>> api_response({"foo": "bar"}, 200)

    """
    try:
        body = json.dumps(body, default=cast_default, ensure_ascii=False)
    except Exception as details:
        print(str(details))
        raise details
    else:
        response = {
            "statusCode": status_code,
            "body": body,
            "headers": {"Access-Control-Allow-Origin": "*"},
        }
        return response
