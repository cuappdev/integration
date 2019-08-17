from os import environ
from subprocess import call

import requests

"""
Class describing a test object, with an optional closure.
"""
class Test:
    def __init__(self, **kwargs):
        self.app = kwargs['app']
        self.callback = kwargs.get('callback', lambda r: True)
        self.name = kwargs['name']
        self.url = kwargs['url']

    def run_test(self):
        r = requests.get(test.url)
        return r.status_code == 200 and test.callback(r)

ithaca_transit_tests = [
    Test(
        app='Transit',
        url='http://transit-backend.cornellappdev.com/api/docs/',
        name='Transit Docs 200 test'
    ),
    Test(
        app='Transit',
        url='http://transit-backend.cornellappdev.com/api/v1/allstops/',
        name='Transit AllStops 200 test'
    ),
]

if __name__ == '__main__':
    tests = ithaca_transit_tests

    num_tests = len(tests)
    num_failures = 0
    seen_tests = set()
    curl_body = ""

    for test in tests:
        if test.app not in seen_tests:
            curl_body += "Running tests for {}...\n".format(test.app)
            curl_body += "```\n"
            seen_tests.add(test.app)

        if test.run_test():
            curl_body += "{}: Success\n".format(test.name)
        else:
            curl_body += "{}: Failure\n".format(test.name)
            num_failures += 1

    curl_body += "```\n"
    curl_body += "*Summary: {}/{} tests passed!*".format(num_tests, num_tests - num_failures)

    CURL_PREFIX = """curl -X POST -H 'Content-type: application/json' --data """
    CURL_BODY = """'{{ "text": "{}" }}'""".format(curl_body)

    call(CURL_PREFIX + CURL_BODY + " " + environ['SLACK_HOOK_URL'], shell=True)
