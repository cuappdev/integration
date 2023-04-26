from enum import Enum, auto
import json
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
        self.should_send = True


class Config:
    """
    Config defines a configuration for each tested app containing whether the app tests
    are <ON>, <OFF>, or <FAILED>. Note: In main.py, apps that are mapped to <FAILED> will be
    tested but will not ping slack users. If the tests succeed, then the app will
    be mapped to <ON>.
    """

    SETTINGS = ["ON", "OFF", "FAILED"]

    def __init__(self, config_json):
        self._config = {}
        
        for config in config_json[1:-1].split(","):
            k, v = config.split(": ")
            self._config[k] = v

    @classmethod
    def create_default_config(cls, test_groups):
        default_json = json.dumps({app.name: "ON" for app in test_groups})
        return cls(default_json)

    def __len__(self):
        return len(self._config)

    def __str__(self):
        return json.dumps(self._config)

    def get(self, app_name):
        return self._config.get(app_name)

    def set(self, app_name, setting):
        if setting in self.SETTINGS and app_name in self._config.keys():
            self._config[app_name] = setting
            return True
        else:
            return False
