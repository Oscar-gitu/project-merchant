# -*- coding: utf-8 -*-
import json
import os
import sys
import traceback
from functools import partial, wraps
from typing import Any, Callable, Dict
from urllib.parse import (
    quote,
    quote_plus,
)

import requests
import wrapt
from aws_lambda_powertools import Logger
from core_api.responses import (
    api_response,
)
from core_api.utils import (
    get_body,
    get_status_code,
)
from core_aws.lambdas import (
    create_context,
)
from core_aws.logs import event_registry
from core_aws.ssm import get_parameter
from core_utils.environment import (
    ENVIRONMENT,
    LAMBDA_NAME,
    LAMBDA_STREAM_NAME,
    REGION,
)

try:
    if not os.getenv("DEVELOPER"):
        print("patching...")

        from aws_xray_sdk.core import (
            patch_all,
        )

        patch_all()
except Exception as e:
    print(str(e))

__ALL__ = [
    'lambda_interceptor',
]

HOST_SLACK = "https://hooks.slack.com/services"


def get_response(response, logger):
    try:
        return response.text
    except Exception as e:
        logger.warning(f"Error to try return response like text: {e}")
        return response.content


class SingletonPatchRequestMeta(type):
    _instances: Dict[str, Any] = {}

    def __call__(cls, *args, **kwargs):
        cls.__event = args[0]
        cls.__logger = args[1]
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance

            def wrapper(wrapped, instance, args, kwargs):
                """
                Patch the requests module

                Args:
                    wrapped:
                    instance:
                    args:
                    kwargs:

                Returns:
                """
                response = wrapped(*args, **kwargs)

                url = kwargs.pop("url", None)

                if response.ok and str(url).startswith(HOST_SLACK):
                    return response
                try:
                    _event = {"service": cls.__logger.service, "event": cls.__event}

                    _event.update({"Arguments for request": args,
                                   "response": get_response(response, cls.__logger)} if not url else {
                        "Requests to": url,
                        "Parameters for request": kwargs,
                        "response": get_response(response, cls.__logger)
                    })

                    _event.update({"Response Status Code": response.status_code})
                    country = os.environ.get('COUNTRY')
                    log_group = f"{ENVIRONMENT.lower()}-{country.lower()}-LogGroupSecretAPI"

                    event_registry(log_group, LAMBDA_STREAM_NAME, _event)
                except Exception as e:
                    cls.__logger.error(e)

                return response

            try:
                wrapt.wrap_function_wrapper("requests", "Session.request", wrapper)
            except Exception as e:
                cls.__logger.info(e)
        return cls._instances[cls]


class PatchRequest(metaclass=SingletonPatchRequestMeta):
    def __init__(self, event, logger):
        self.event = event


def __is_a_lambda_execution():
    is_linux = False

    if os.name == 'posix' or os.environ.get('LOGGER_TEST') == "yes":
        is_linux = True

    return LAMBDA_NAME and is_linux


def __parse_error_to_slack(message_error):
    url_log = f"https://{quote(REGION)}.console.aws.amazon.com/cloudwatch/home?region={quote(REGION)}#logsV2:log-groups/log-group/$252Faws$252Flambda$252F{quote(LAMBDA_NAME)}/log-events/{quote_plus(LAMBDA_STREAM_NAME)}"

    error = json.dumps({
        "username": "Merchant Platform",
        "icon_emoji": ":loudspeaker:",
        "attachments": [
            {
                "color": "#DF0101",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": LAMBDA_NAME
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "plain_text",
                            "text": "Mensaje"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"```{message_error}```"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Log completo en CloudWatch\n_Deberás tener una sesión activa en la cuenta de AWS_"
                        },
                        "accessory": {
                            "type": "button",
                            "text":
                                {
                                    "type": "plain_text",
                                    "text": "Ir"
                                },
                            "url": url_log,
                            "action_id": "button-action"
                        }
                    }
                ]
            }
        ]
    })

    return error


def __slack_notification(error, stack, logger):
    if __is_a_lambda_execution():
        message_error = f"{str(error)}\n"

        try:
            for e in stack or []:
                if "File" in e:
                    path = e.split()[1]
                    e = e.replace(path, os.path.split(e.split()[1])[-1])
                    e = e.replace("File", "File:")
                    e = e.replace("line", "Line:")
                    e = e.replace('"', "")
                    message_error += f"\n{e.strip()}"

            headers = {'Content-Type': "application/json"}
            message_error = __parse_error_to_slack(message_error)
            url = f"{HOST_SLACK}{get_parameter(f'/config/infra/{ENVIRONMENT.lower()}/slack-notification', is_dict=False)}"

            response = requests.post(url, data=message_error, headers=headers)

            if not response.ok:
                logger.info("Slack Notification")
                logger.info(response.content)
        except Exception as e:
            logger.info("Slack Notification Error")
            logger.info(e)

        logger.error(message_error)


def __notify_error(error, stack, logger):
    logger.error("A no managed error was raised")
    __slack_notification(error, stack, logger)


def __notify_manage_error(error, logger):
    logger.error("A managed error was raised")
    logger.error(error)
    __slack_notification(error, None, logger)


def __manage_response(response: Any, logger: Logger):
    status_code = get_status_code(response)

    if status_code >= 300:
        __notify_manage_error(f"{status_code} - {json.dumps(get_body(response))}", logger)

    return response


def lambda_interceptor(function: Callable[[Dict, Any], Any] = None, logger: Logger = None, manage_raise: bool = True):
    """
    With this decorator, functions and constants are injected into the context of the lambda, in turn it can receive a function to
    parse the lambda response, receive a function to parse the lambda event and / or a model that validates its structure

    Args:
        function: Callable object, you dont need pass explicitly to function.
        logger: required, a Logger object, preferably derived from the aws_lambda_powertools module, you can use the get_logger function
        manage_raise: By default true, If this flag is true all exceptions not managed willbe catch and manage by this decorator.

    Returns:
    """
    if not logger:
        raise AttributeError('logger is required')
    if function is None:
        return partial(lambda_interceptor, logger=logger, manage_raise=manage_raise)

    @wraps(function)
    def decorator(event, context):
        if event.get("headers", {}).get("HealthCheck"):
            return api_response({"message": "HealthCheck success"}, 200)
        PatchRequest(event, logger)
        context = context if context else create_context(logger.service)

        try:
            response = function(event, context)
        except Exception as e:
            exc_type, exc_value, exc_tb = sys.exc_info()
            stack = traceback.format_exception(exc_type, exc_value, exc_tb)

            __notify_error(e, stack, logger)

            if manage_raise:
                return api_response({"message": "Internal Server Error"}, 500)
            else:
                raise e
        else:
            res = __manage_response(response, logger)
            logger.info({"lambda response": res})

            return res

    return decorator
