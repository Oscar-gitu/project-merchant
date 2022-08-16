# -*- coding: utf-8 -*-
import json
import os
from decimal import Decimal

import peewee
from core_db.base_model import database
from core_db.models import (
    MerchantCallback,
    MtsRequestLog,
)
from core_utils.custom_requests import (
    AbstractRequest,
)
from core_utils.utils import get_logger

LOGGER = get_logger("core_db.utils")


def _query_validate_refound(sub_type, transaction, client_id, wallet_client_id):
    country = os.getenv('COUNTRY')
    return MtsRequestLog.select(MtsRequestLog.response).where(
        (MtsRequestLog.country == country) & (MtsRequestLog.transaction_id == transaction) & (
                MtsRequestLog.sub_type == sub_type) & (MtsRequestLog.client_id == client_id) & (
                MtsRequestLog.wallet_client_id == wallet_client_id)).dicts()


def is_valid_refound(amount_to_refound, transaction, client_id, wallet_client_id):
    result = _query_validate_refound("otpconfirm", transaction, client_id, wallet_client_id).get()
    refound_result = _query_validate_refound("refound", transaction, client_id, wallet_client_id).get_all()

    amount = Decimal(json.loads(result)["amount"])
    refounds = sum([Decimal(json.loads(n)["amount"]) for n in refound_result])
    return (refounds <= amount) and ((amount - refounds) >= amount_to_refound)


def mts_request_record(external_id, amount, sub_type, client_id, response, transaction_id=None, wallet_client_id=None,
                       country=None, metadata=None):
    with database.atomic():
        try:
            MtsRequestLog.insert(
                external_id=external_id,
                sub_type=sub_type,
                amount=amount,
                client_id=client_id,
                response=response,
                transaction_id=transaction_id,
                wallet_client_id=wallet_client_id,
                country=country,
                metadata=metadata
            ).execute()
        except Exception as e:
            LOGGER.error(str(e))
            database.rollback()
            LOGGER.error(
                f"""
                        Request data with error.
                        {external_id}
                        {sub_type}
                        {amount}
                        {client_id}
                        {response}
                        {transaction_id}
                        {wallet_client_id}
                        {country}
                        {metadata}
            """
            )


class CallbackRequest(AbstractRequest):
    def __init__(self, merchant_id, override_info):
        self.__callback_data(merchant_id)
        self.__override_info = override_info

    def get_body(self):
        try:
            body = self.__override_data_for_callback(self.__callback_data.get("body"))
            body = json.loads("{%s}" % body)
        except Exception as e:
            LOGGER.warning(str(e))
            return None
        return body

    def get_headers(self):
        try:
            headers = self.__override_data_for_callback(self.__callback_data.get("headers"))
            headers = json.loads("{%s}" % headers)
        except Exception as e:
            LOGGER.warning(str(e))
            return None
        return headers

    def get_params(self):
        try:
            params = self.__override_data_for_callback(self.__callback_data.get("params"))
            params = json.loads("{%s}" % params)
        except Exception as e:
            LOGGER.warning(str(e))
            return None
        return params

    def get_method_and_url(self):
        try:
            method = self.__callback_data.get("method")
            url = self.__callback_data.get("url")
        except Exception as e:
            LOGGER.warning(str(e))
            return None
        return method, f"{url}"

    def get_name(self):
        try:
            app_name = self.__callback_data.get("app_name")
        except Exception as e:
            LOGGER.warning(str(e))
            return None
        return app_name

    def get_message(self):
        try:
            message = self.__callback_data.get("message")
        except Exception as e:
            LOGGER.warning(str(e))
            return None
        return message

    def __callback_data(self, merchant_id):
        with database.atomic() as t:
            try:
                self.__callback_data = MerchantCallback.select().where(MerchantCallback.id == merchant_id).dicts().get()
            except MerchantCallback.DoesNotExist:
                t.rollback()
                raise self.MerchantNotExistsException()
            except peewee.DataError:
                t.rollback()
                raise self.InvalidMerchantException()

        self.redirect_url = self.__callback_data.get("redirect")

    def __override_data_for_callback(self, part):
        return part.format(**self.__override_info)

    class MerchantNotExistsException(Exception):
        def __init__(self):
            super().__init__(self, "Merchant not exist")

    class InvalidMerchantException(Exception):
        def __init__(self):
            super().__init__(self, "Invalid merchant")
