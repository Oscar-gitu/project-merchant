# -*- coding: utf-8 -*-
import uuid


def create_context(function_name):
    """
    Create a context for a lambda function.

    Parameters
    ----------
    function_name : str

    Returns
    -------
    Type: context for a lambda function


    Examples
    --------
    >>> from core_aws.lambdas import create_context
    >>> create_context("lambda_function_name")

    """
    definition = {
        "get_remaining_time_in_millis": lambda: 30000,
        "function_name": function_name,
        "aws_request_id": str(uuid.uuid4()),
    }
    return type("Context", (), definition)
