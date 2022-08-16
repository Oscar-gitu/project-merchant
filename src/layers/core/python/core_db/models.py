# -*- coding: utf-8 -*-
from core_db.base_model import BaseModel
from peewee import (
    SQL,
    BigAutoField,
    BooleanField,
    CharField,
    DateTimeField,
    DecimalField,
    ForeignKeyField,
    IntegerField,
    TextField,
    UUIDField,
)
from playhouse.postgres_ext import (
    JSONField,
)

SCHEMA = "merchant"

__all__ = [
    "Currency",
    "Country",
    "Role",
    "Owner",
    "Account",
    "AccountForm",
    "Topic",
    "Question",
    "Answer",
    "Permission",
    "RolePermission",
    "Store",
    "User",
    "UserStore",
    "CountryCurrency",
    "Transaction",
    "MtsRequestLog",
    "MerchantCallback",
    "MtsCronTransaction",
    "MtsCronTransactionType"
]

UUID4 = "DEFAULT uuid_generate_v4()"
NOW = "DEFAULT now()"
FALSE = "DEFAULT false"


class MtsRequestLog(BaseModel):
    id = BigAutoField()
    external_id = TextField(null=True)
    sub_type = TextField(null=True)
    amount = TextField(null=True)
    client_id = TextField(null=True)
    response = JSONField(null=True)
    created_at = DateTimeField(constraints=[SQL(NOW)], index=True, null=True)
    updated_at = DateTimeField(null=True)
    transaction_id = TextField(null=True)
    wallet_client_id = TextField(null=True)
    country = TextField(null=True)
    metadata = JSONField(null=True)

    class Meta:
        table_name = 'MtsRequestLog'
        indexes = (
            (('country', 'sub_type', 'client_id', 'external_id', 'transaction_id', 'amount'), False),
            (('country', 'sub_type', 'client_id', 'wallet_client_id', 'response'), False),
            (('country', 'sub_type', 'external_id', 'transaction_id', 'response'), False),
            (('created_at', 'id', 'created_at', 'amount', 'external_id', 'transaction_id', 'response', 'client_id', 'wallet_client_id'), False),
        )
        schema = SCHEMA


class Country(BaseModel):
    id = BigAutoField()
    name = TextField(null=True)
    short_name = TextField(null=True)
    created_at = DateTimeField(constraints=[SQL(NOW)], null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = "Country"
        schema = SCHEMA


class Role(BaseModel):
    id = BigAutoField()
    name = TextField(null=True)
    description = TextField(null=True)
    created_at = DateTimeField(constraints=[SQL(NOW)], null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = "Role"
        schema = SCHEMA


class Owner(BaseModel):
    id = UUIDField(constraints=[SQL(UUID4)], primary_key=True)
    email = TextField(null=True)
    names = TextField(null=True)
    first_name = TextField(null=True)
    second_name = TextField(null=True)
    role = ForeignKeyField(column_name="role_id", field="id", model=Role, null=True)
    msnd_id = IntegerField(null=True)
    organization_name = TextField(null=True)
    country = ForeignKeyField(
        column_name="country_id", field="id", model=Country, null=True
    )
    created_at = DateTimeField(constraints=[SQL(NOW)], null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = "Owner"
        schema = SCHEMA


class Account(BaseModel):
    id = UUIDField(constraints=[SQL(UUID4)], primary_key=True)
    owner = ForeignKeyField(column_name="owner_id", field="id", model=Owner, null=True)
    account = JSONField(null=True)
    is_deleted = BooleanField(null=True)
    is_principal = BooleanField(null=True)
    created_at = DateTimeField(constraints=[SQL(NOW)], null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = "Account"
        schema = SCHEMA


class AccountForm(BaseModel):
    id = BigAutoField()
    country = ForeignKeyField(
        column_name="country_id", field="id", model=Country, null=True
    )
    json_form = JSONField(null=True)
    created_at = DateTimeField(constraints=[SQL(NOW)], null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = "Account_Form"
        schema = SCHEMA


class Topic(BaseModel):
    id = BigAutoField()
    name = TextField(null=True)
    created_at = DateTimeField(constraints=[SQL(NOW)], null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = "Topic"
        schema = SCHEMA


class Question(BaseModel):
    id = BigAutoField()
    topic = ForeignKeyField(column_name="topic_id", field="id", model=Topic, null=True)
    question = TextField(null=True)
    country = ForeignKeyField(
        column_name="country_id", field="id", model=Country, null=True
    )
    created_at = DateTimeField(constraints=[SQL(NOW)], null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = "Question"
        schema = SCHEMA


class Answer(BaseModel):
    id = BigAutoField()
    answer = TextField(null=True)
    question = ForeignKeyField(
        column_name="question_id", field="id", model=Question, null=True
    )
    created_at = DateTimeField(null=True)
    update_at = DateTimeField(null=True)

    class Meta:
        table_name = "Answer"
        schema = SCHEMA


class Currency(BaseModel):
    id = BigAutoField()
    name = TextField(null=True)
    created_at = DateTimeField(constraints=[SQL(NOW)], null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = "Currency"
        schema = SCHEMA


class CountryCurrency(BaseModel):
    id = BigAutoField()
    country = ForeignKeyField(
        column_name="country_id", field="id", model=Country, null=True
    )
    currency = ForeignKeyField(
        column_name="currency_id", field="id", model=Currency, null=True
    )
    created_at = DateTimeField(constraints=[SQL(NOW)], null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = "Country_Currency"
        schema = SCHEMA


class Permission(BaseModel):
    id = BigAutoField()
    name = TextField(null=True)
    policy = JSONField(null=True)
    created_at = DateTimeField(constraints=[SQL(NOW)], null=True)
    update_at = DateTimeField(null=True)

    class Meta:
        table_name = "Permission"
        schema = SCHEMA


class RolePermission(BaseModel):
    id = BigAutoField()
    role = ForeignKeyField(column_name="role_id", field="id", model=Role, null=True)
    permission = ForeignKeyField(
        column_name="permission_id", field="id", model=Permission, null=True
    )
    created_at = DateTimeField(constraints=[SQL(NOW)], null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = "Role_Permission"
        schema = SCHEMA


class Store(BaseModel):
    id = UUIDField(constraints=[SQL(UUID4)], primary_key=True)
    store_key = CharField(null=True)
    name = TextField(null=True)
    owner = ForeignKeyField(column_name="owner_id", field="id", model=Owner, null=True)
    is_deleted = BooleanField(null=True)
    created_at = DateTimeField(constraints=[SQL(NOW)], null=True)
    updated_at = DateTimeField(null=True)
    is_deleted = BooleanField(constraints=[SQL("DEFAULT false")], null=True)

    class Meta:
        table_name = "Store"
        schema = SCHEMA
        constraints = [SQL("UNIQUE (name, owner)")]


class User(BaseModel):
    id = UUIDField(constraints=[SQL(UUID4)], primary_key=True)
    email = TextField(null=True)
    names = TextField(null=True)
    first_name = TextField(null=True)
    second_name = TextField(null=True)
    role = ForeignKeyField(column_name="role_id", field="id", model=Role, null=True)
    owner = ForeignKeyField(column_name="owner_id", field="id", model=Owner, null=True)
    is_deleted = BooleanField(null=True)
    created_at = DateTimeField(constraints=[SQL(NOW)], null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = "User"
        schema = SCHEMA


class UserStore(BaseModel):
    id = BigAutoField()
    store = ForeignKeyField(column_name="store_id", field="id", model=Store, null=True)
    user = ForeignKeyField(column_name="user_id", field="id", model=User, null=True)
    created_at = DateTimeField(constraints=[SQL(NOW)], null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = "User_Store"
        schema = SCHEMA


class Transaction(BaseModel):
    id = BigAutoField()
    amount = DecimalField(null=True)
    status = TextField(null=True)
    account = ForeignKeyField(
        column_name="account_id", field="id", model=Account, null=True
    )
    owner = ForeignKeyField(column_name="owner_id", field="id", model=Owner, null=True)
    created_at = DateTimeField(constraints=[SQL(NOW)], null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = "Transaction"
        schema = SCHEMA


class MerchantCallback(BaseModel):
    id = UUIDField(constraints=[SQL(UUID4)], primary_key=True)
    method = TextField(null=True)
    url = CharField(null=True)
    params = CharField(null=True)
    headers = CharField(null=True)
    body = CharField(null=True)
    redirect = CharField(null=True)
    created_at = DateTimeField(constraints=[SQL(NOW)], null=True)
    updated_at = DateTimeField(null=True)
    app_name = CharField(null=True)
    message = CharField(null=True)
    is_deleted = BooleanField(constraints=[SQL(FALSE)], null=True)

    class Meta:
        table_name = "MerchantCallback"
        schema = SCHEMA


class MtsCronTransactionType(BaseModel):
    id = BigAutoField()
    name = TextField(null=True)
    is_deleted = BooleanField(constraints=[SQL(FALSE)], null=True)

    class Meta:
        table_name = "MtsCronTransactionType"
        schema = SCHEMA


class MtsCronTransaction(BaseModel):
    id = UUIDField(constraints=[SQL(UUID4)], primary_key=True)
    merchant_id = TextField(null=True)
    type = ForeignKeyField(
        column_name="type", field="id", model=MtsCronTransactionType, null=True
    )
    data = JSONField(null=True)
    cron = TextField(null=True)
    is_deleted = BooleanField(constraints=[SQL(FALSE)], null=True)
    created_at = DateTimeField(constraints=[SQL(NOW)], null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = "MtsCronTransaction"
        schema = SCHEMA
