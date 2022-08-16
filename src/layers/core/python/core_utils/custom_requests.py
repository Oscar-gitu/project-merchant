from abc import ABC, abstractmethod

import requests


class AbstractRequest(ABC):
    def request(self):
        query_params = self.get_params()
        headers = self.get_headers()
        body = self.get_body()
        method = self.get_method()
        url = self.get_url()
        if not method or not url:
            method, url = self.get_method_and_url()
        return requests.request(method, url, params=query_params, headers=headers, json=body)

    @abstractmethod
    def get_params(self) -> dict:
        pass

    @abstractmethod
    def get_headers(self) -> dict:
        pass

    @abstractmethod
    def get_body(self) -> dict:
        pass

    def get_method(self) -> str:
        pass

    def get_url(self) -> str:
        pass

    def get_method_and_url(self) -> tuple:
        pass


def custom_request(abstract_request: AbstractRequest):
    return abstract_request.request()
