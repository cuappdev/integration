import requests

"""
TestGroup defines a set of tests to be run for a specific application.
"""
class TestGroup:
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.tests = kwargs['tests']

"""
Test defines a test object, with an optional closure. More information on [closure] is
specified below.
"""
class Test:
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.url = kwargs['url']

        # An optional closure. This allows a user to define a function [f: request -> bool]
        # to perform any additional operations. For example, a user could check the format
        # of a response, or verify that certain data is included.
        # If the value is not provided, a lambda that returns True is the default.
        self.callback = kwargs.get('callback', lambda r: True)

    def is_success(self):
        r = requests.get(self.url)
        return r.status_code == 200 and self.callback(r)
