# -*- coding: utf-8 -*-
import logging

import boto3
from botocore.exceptions import (
    ClientError,
)

__all__ = [
    "update_item",
]

dynamodb = boto3.client("dynamodb")


def update_item(*, table, key, update):
    """Update item in a table

    Args:
        table (str): The name of the table containing the item to update.
        key (dict): The primary key of the item to be updated. Each element consists of an attribute name and a value for that attribute.
                   {
                        'string': {
                            'S': 'string',
                            'N': 'string',
                            'B': b'bytes',
                            'SS': [
                                'string',
                            ],
                            'NS': [
                                'string',
                            ],
                            'BS': [
                                b'bytes',
                            ],
                            'M': {
                                'string': {'... recursive ...'}
                            },
                            'L': [
                                {'... recursive ...'},
                            ],
                            'NULL': True|False,
                            'BOOL': True|False
                        }
                    }
        update (dict): An expression that defines one or more attributes to be updated, the action to be performed on them, and new values for them.
                   {
                        'string': {
                            'Value': {
                                'S': 'string',
                                'N': 'string',
                                'B': b'bytes',
                                'SS': [
                                    'string',
                                ],
                                'NS': [
                                    'string',
                                ],
                                'BS': [
                                    b'bytes',
                                ],
                                'M': {
                                    'string': {'... recursive ...'}
                                },
                                'L': [
                                    {'... recursive ...'},
                                ],
                                'NULL': True|False,
                                'BOOL': True|False
                            },
                            'Action': 'ADD'|'PUT'|'DELETE'
                        }
                    }

    Returns:
        dict: Returns all of the attributes of the item, as they appear after the UpdateItem operation.
    """
    try:
        response = dynamodb.update_item(
            TableName=table,
            Key=key,
            AttributeUpdates=update,
        )

    except ClientError as e:
        logging.error(e)
        return None

    logging.debug(response)

    if not response:
        return None

    return response
