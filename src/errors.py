import requests


class UnexpectedServerResponseException(Exception):
    def __init__(self, response: requests.Response):
        self.status_code = response.status_code
        self.body = response.text
