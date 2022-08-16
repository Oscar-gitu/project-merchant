# -*- coding: utf-8 -*-
import json
import time

import boto3
from botocore.exceptions import (
    ClientError,
)
from core_utils.utils import get_logger

LOGGER = get_logger("core_aws.logs")
client = boto3.client('logs')


def event_registry(log_group, log_stream, event):
    """Uploads a batch of log events to the specified log stream.

    Args:
        log_group (str): The name of the log group
        log_stream (str): The name of the log stream
        event (dict): The event message (is serialized in the function)

    Returns:
        bool: successful execution
    """
    try:
        client.create_log_stream(logGroupName=log_group, logStreamName=log_stream)
    except client.exceptions.ResourceAlreadyExistsException:
        pass

    try:
        response = client.describe_log_streams(logGroupName=log_group, logStreamNamePrefix=log_stream)

        event_log = {
            'logGroupName': log_group,
            'logStreamName': log_stream,
            'logEvents': [
                {
                    'timestamp': int(round(time.time() * 1000)),  # solo con este time se agregaron los eventos al log, con otros no funciona (termina bien pero no quedan registrados)
                    'message': json.dumps(event)
                }
            ],
        }

        if 'uploadSequenceToken' in response['logStreams'][0]:
            event_log.update({'sequenceToken': response['logStreams'][0]['uploadSequenceToken']})

        response = client.put_log_events(**event_log)
    except ClientError as e:
        LOGGER.error(e)
        return False

    LOGGER.debug(str(response))
    return True
