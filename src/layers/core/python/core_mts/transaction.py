# -*- coding: utf-8 -*-
import json
from datetime import datetime

import core_aws.ssm
import core_db.utils
import core_mts.provider
from core_db.base_model import database
from core_db.models import MtsRequestLog
from core_utils.environment import (
    ENVIRONMENT,
)
from core_utils.utils import get_logger

__all__ = [
    "convert_transaction_response",
]

LOGGER = get_logger("core_mts.transaction")


def convert_transaction_response(index, transaction, msisdn):
    """Convert payload mts response to integrator one
    :param index int
    :param transaction dict
    :param msisdn str
    :return dict
    """
    payment_date, pay_time = payment_movement_date_time(transaction)
    return {
        "recordNo": index,
        "paymentDate": payment_date,
        "payTime": pay_time,
        "amount": transaction['amount'],
        "reference": transaction['transactionReference'],
        "transactionId": transaction['transactionReference'],
        "status": transaction['transactionStatus'],
        "msisdn": msisdn
    }


def payment_movement_date_time(transaction):

    try:
        movement_date = list(filter(lambda t: t["type"] == "1", transaction['movements']))
        payment_datetime = datetime.strptime(movement_date[0]['movementDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
        payment_date = payment_datetime.strftime('%Y-%m-%d')
        pay_time = payment_datetime.strftime('%H:%M:%S')

        return payment_date, pay_time
    except (IndexError, TypeError, ValueError):
        return '', ''


def find_log_data(*, country, sub_type, external_id, transaction_id):
    """Find the transaction data in MtsRequestLog
    More parameters can be added with their respective validations if necessary

    Args:
        country (str): country
        sub_type (str): subtype of the data to be searched
        external_id (str): external id
        transaction_id (str): transaction id


    Returns:
        dict: only cone record with the columns: response and metadata
        More fields can be added if necessary
    """
    with database.atomic():
        try:
            condition = (
                (MtsRequestLog.country == country if not None else MtsRequestLog.country)
                & (MtsRequestLog.sub_type == sub_type if not None else MtsRequestLog.sub_type)
                & (MtsRequestLog.external_id == external_id if not None else MtsRequestLog.external_id)
                & (MtsRequestLog.transaction_id == transaction_id if not None else MtsRequestLog.transaction_id)
            )

            result = (
                (
                    MtsRequestLog
                    .select(MtsRequestLog.response, MtsRequestLog.metadata)
                    .where(condition)
                    .order_by(MtsRequestLog.created_at.desc())
                )
                .dicts()
                .get()
            )
        except MtsRequestLog.DoesNotExist:
            return None

        return result


def validation_reverse(country, mts_host, mts_api_key, mts_authorization, external_id, transaction_id, reverse_date_request):
    TRANSACTION_TYPE = "INFO"

    try:
        time_per_country = core_aws.ssm.get_parameter(f"/{ENVIRONMENT.lower()}/{country}/api/connector/time-per-country", is_dict=False)

        if not time_per_country:
            status_code = 400
            message = "Time per country not found"
            return status_code, message

        url = f"{mts_host}/transactions/{transaction_id}"

        headers = {
            "Content-Type": "application/json",
            "x-api-key": mts_api_key,
            "Authorization": mts_authorization
        }

        response = core_mts.provider.call_request(method="GET", url=url, headers=headers)
        core_db.utils.mts_request_record(external_id, None, TRANSACTION_TYPE, None, response.text, transaction_id=transaction_id, country=country)

        message = "success"
        status_code = response.status_code

        if status_code != 200:
            message = core_mts.provider.get_message_response(response)
            return status_code, message

        data_transaction = response.json()
        confirm_transaction_request = datetime.fromisoformat(data_transaction["requestDate"][0:23])  # cuts the string short of the "Z INFO"

        if (int(time_per_country) < (reverse_date_request - confirm_transaction_request).days):
            status_code = 400
            message = "Transaction time reverse expired"

        return status_code, message
    except Exception as e:
        LOGGER.error(e)
        raise ValueError(e)


def reverse(country, mts_host, mts_api_key, mts_authorization, external_id, transaction_id, request_date, reason):
    """Creates a complete reversal of a transaction

    Args:
        country (str): country
        mts_host (str): where the service to be consumed is hosted
        mts_api_key (str): identifier that serves as the means of authentication of a user
        mts_authorization (str): token to authenticate a user
        external_id (str): external id
        transaction_id (str): transaction id
        request_date (str): date of request
        reason (str): reason for request

    Raises:
        ValueError: error generated not controlled

    Returns:
        tuple:  status_code, message
    """
    TRANSACTION_TYPE = "REVERSAL"

    try:
        status_code = 201
        message = "success"

        # validates if a reverse side already exists in the database with that transaction id
        reverse_confirm = find_log_data(country=country, sub_type=TRANSACTION_TYPE, external_id=external_id, transaction_id=transaction_id)

        if reverse_confirm:
            status_confirm = json.loads(reverse_confirm["response"]).get("transactionStatus", None)

            if status_confirm and status_confirm.lower() == "ok":
                return status_code, message

        # an invocation is generated to create the reverse side of the transaction
        url = f"{mts_host}/transactions/{transaction_id}/reversals"

        headers = {
            "Content-Type": "application/json",
            "x-api-key": mts_api_key,
            "Authorization": mts_authorization
        }
        body = {
            "type": TRANSACTION_TYPE,
            "requestDate": int(datetime.timestamp(request_date)),
            "metadata": [{
                "key": "externalDetails",
                "value": external_id
            }]
        }
        metadata = {"reason": reason}

        response = core_mts.provider.call_request(method="POST", url=url, body=body, headers=headers)
        core_db.utils.mts_request_record(external_id, None, TRANSACTION_TYPE, None, response.text, transaction_id=transaction_id, country=country, metadata=metadata)

        status_code = response.status_code

        if status_code != 201:
            message = core_mts.provider.get_message_response(response)

        return status_code, message
    except Exception as e:
        LOGGER.error(e)
        raise ValueError(e)
