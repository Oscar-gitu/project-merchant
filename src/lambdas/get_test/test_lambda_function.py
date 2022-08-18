from unittest import TestCase
from core_api.utils import get_status_code, get_body
from .lambda_function import (
    lambda_handler
)


class Test(TestCase):

    def test_lambda_handler_200(self):
        response = lambda_handler(None, None)
        _body = get_body(response)
        _status = get_status_code(response)

        self.assertEqual(200, _status)
        self.assertIsInstance(_body, dict)