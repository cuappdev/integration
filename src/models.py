from enum import Enum, auto
import requests


class TestGroup:
    """
    TestGroup defines a set of tests to be run for a specific application.
    """

    def __init__(self, **kwargs):
        self.application = kwargs["application"]
        self.name = kwargs["name"]
        self.slack_message = SlackMessage(text="")
        self.tests = kwargs["tests"]


class Request:
    """
    Request defines a python [request] object.
    """

    def __init__(self, **kwargs):
        self.method = kwargs["method"]
        self.url = kwargs["url"]
        self.payload = kwargs.get("payload")

    def call(self):
        if self.method == "GET":
            return requests.get(self.url, params=self.payload, timeout=15)
        if self.method == "POST":
            return requests.post(self.url, json=self.payload, timeout=15)

        # More method types can be added here...
        raise Exception("Unsupported method type!")


class Result(Enum):
    """
    Result defines the result of running a test.
    """

    SUCCESS = auto()
    ERROR = auto()
    TIMEOUT = auto()


class Application(Enum):
    """
    Application defines which application a test group belongs to.
    """

    EATERY = auto()
    TRANSIT = auto()
    UPLIFT = auto()
    COURSEGRAB = auto()
    VOLUME = auto()


class Test:
    """
    Test defines a test object, with an optional closure. More information on [closure] is
    specified below.
    """

    def __init__(self, **kwargs):
        self.name = kwargs["name"]
        self.request = kwargs["request"]

        # An optional closure. This allows a user to define a function [f: request -> bool]
        # to perform any additional operations. For example, a user could check the format
        # of a response, or verify that certain data is included.
        # If the value is not provided, a lambda that returns True is the default.
        self.callback = kwargs.get("callback", lambda r: True)

    def get_result(self):
        try:
            r = self.request.call()
            if r.status_code == 200 and self.callback(r):
                return Result.SUCCESS
            return Result.ERROR
        except requests.exceptions.Timeout:
            return Result.TIMEOUT
        except requests.exceptions.RequestException:
            return Result.ERROR


class SlackMessage:
    """
    SlackMessage defines a slack message object which contains information on whether a
    message should send and the contents of the message.
    """

    def __init__(self, **kwargs):
        self.text = kwargs["text"]
        self.should_send = False
