# -*- coding: utf-8 -*-
from core_api.responses import (
    api_response,
)


def lambda_handler(event, context):
    return api_response({"message": "test"}, 200)
