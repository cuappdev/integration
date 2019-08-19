import time
from os import environ

from models import Request, Test, TestGroup

BASE_URL = environ['TRANSIT_BACKEND_URL']

tests = [
    Test(
        name='api/docs 200',
        request=Request(
            method='GET',
            url=BASE_URL + 'api/docs/',
        ),
    ),
    Test(
        name='api/v1/allstops 200',
        request=Request(
            method='GET',
            url=BASE_URL + 'api/v1/allstops/',
        ),
    ),
    Test(
        name='api/v2/route 200',
        request=Request(
            method='POST',
            url=BASE_URL + 'api/v2/route/',
            payload={
                "arriveBy": False,
                "end": "42.454197,-76.440651",
                "start": "42.449086,-76.483306",
                "destinationName": 933,
                "time": time.time(),
            }
        ),
    ),
    Test(
        name='api/v2/route does not contain -1',
        request=Request(
            method='POST',
            url=BASE_URL + 'api/v2/route/',
            payload={
                "arriveBy": False,
                "end": "42.454197,-76.440651",
                "start": "42.449086,-76.483306",
                "destinationName": 933,
                "time": time.time(),
            }
        ),
        callback=lambda r: not '''"routeNumber":null''' in r.text,
    ),
]

transit_tests = TestGroup(name='Transit', tests=tests)
