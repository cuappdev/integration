import time
from os import environ

from models import Request, Test, TestGroup

BASE_DEV_URL = environ['TRANSIT_DEV_BACKEND_URL']
BASE_PROD_URL = environ['TRANSIT_BACKEND_URL']

def route_number_non_null_callback(r):
    response = r.json()
    # Make sure response was successful
    if not response['success']:
        return False

    # Iterate over directions
    for route_directions in response['data']['boardingSoon']:
        for direction in route_directions['directions']:
            # Walking directions can have a [None] routeNumber
            if direction['type'] != 'walk' and 'routeNumber' is None:
                return False

    return True

def generate_tests(base_url):
    return [
        Test(
            name='api/docs 200',
            request=Request(
                method='GET',
                url=base_url + 'api/docs/',
            ),
        ),
        Test(
            name='api/v1/allstops 200',
            request=Request(
                method='GET',
                url=base_url + 'api/v1/allstops/',
            ),
        ),
        Test(
            name='api/v2/route 200',
            request=Request(
                method='POST',
                url=base_url + 'api/v2/route/',
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
                url=base_url + 'api/v2/route/',
                payload={
                    "arriveBy": False,
                    "end": "42.454197,-76.440651",
                    "start": "42.449086,-76.483306",
                    "destinationName": 933,
                    "time": time.time(),
                }
            ),
            callback=route_number_non_null_callback
        ),
    ]

transit_dev_tests = TestGroup(name='Transit Dev', tests=generate_tests(BASE_DEV_URL))
transit_prod_tests = TestGroup(name='Transit Prod', tests=generate_tests(BASE_PROD_URL))
