import os
import logging
import boto3
import json
from botocore.exceptions import (
    ClientError,
)

__all__ = [
    "send_queue_message_by_url",
    "send_sqs_message_by_name"
]
LOGGER = logging.getLogger("layer-sqs")


def get_sqs_client():
    return boto3.client("sqs")


def send_queue_message_by_url(queue_url, msg_body=None,
                              message_deduplication_id=None,
                              message_group_id=None):
    """
    Sends a message to the specified queue.

    :param queue_url: String URL of existing SQS queue
    :param msg_body: String message body
    :param message_deduplication_id: String
    :param message_group_id String
    :return: Dictionary containing information about the sent message. If
        error, returns None.
    """
    sqs_client = get_sqs_client()
    try:
        msg = sqs_client.send_message(QueueUrl=queue_url,
                                      MessageBody=json.dumps(msg_body),
                                      MessageDeduplicationId=message_deduplication_id,
                                      MessageGroupId=message_group_id)

    except ClientError:
        LOGGER.error(f'Could not send meessage to the - {queue_url}.')
        return None
    else:
        return msg


def send_sqs_message_by_name(queue_name, msg_body,
                             message_deduplication_id=None, message_group_id=None):
    """

    :param queue_name: String Name of existing SQS queue
    :param msg_body: String message body
    :param message_deduplication_id: String
    :param message_group_id String
    :return: Dictionary containing information about the sent message. If
        error, returns None.
    """

    sqs_client = get_sqs_client()
    sqs_queue_url = sqs_client.get_queue_url(QueueName=queue_name)['QueueUrl']

    try:
        msg = sqs_client.send_message(QueueUrl=sqs_queue_url,
                                      MessageBody=json.dumps(msg_body),
                                      MessageDeduplicationId=message_deduplication_id,
                                      MessageGroupId=message_group_id)
    except ClientError:
        LOGGER.error(f'Could not send meessage to the - {sqs_queue_url}.')
        return None
    return msg

