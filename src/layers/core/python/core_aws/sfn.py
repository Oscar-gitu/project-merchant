import logging
import os
import json
import boto3
from botocore.exceptions import (
    ClientError,
)

__all__ = [
    "execute_sfn",
]
LOGGER = logging.getLogger("layer-sfn")
sfn = boto3.client('stepfunctions')


def execute_sfn(*, name, state_machine_arn, input_value):
    """
        Starts a state machine execution.

        Parameters
        ----------
        name : str
            The name of the execution.This name must be unique
        state_machine_arn : str
            Arn of the state machine to execution.
        input_value : dict
             Input data for the execution.

        Returns
        -------
        dict
            The result of the state machine execution.

        Raises
        ------
        ValueError
            If the state machine arn is not valid.

        Examples
        --------
        >>> from core_aws.sfn import execute_sfn
        >>> get_parameter(stateMachineArn="arn:aws:state:myarn", name="miexecutionname", input={'key':value})

        """
    try:
        response = sfn.start_execution(stateMachineArn=state_machine_arn, name=name, input=json.dumps(input_value))

    except Exception as details:
        LOGGER.warning(details)
        return None

    return response

