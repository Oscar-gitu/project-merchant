# -*- coding: utf-8 -*-
"""
This module contains the Environment class.
"""
import os

ENVIRONMENT = os.environ["ENVIRONMENT"]
DEVELOPER = os.environ.get("DEVELOPER")
LAMBDA_NAME = os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
MTS_API_HOST_dev = os.environ.get("MTS_API_HOST_dev")
REGION = os.environ.get("AWS_REGION")
LAMBDA_STREAM_NAME = os.environ.get("AWS_LAMBDA_LOG_STREAM_NAME")
