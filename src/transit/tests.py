import time
from os import environ

from models import Request, Test, TestGroup

BASE_DEV_URL = environ["TRANSIT_DEV_BACKEND_URL"]
BASE_PROD_URL = environ["TRANSIT_BACKEND_URL"]

# We want to verify that route numbers are non-null, or that they will not show up as
# -1 inside of the application.
def route_number_non_null_callback(r):
    response = r.json()
    # Make sure response was successful
    if not response["success"]:
        return False

    # Iterate over directions
    for route_directions in response["data"]["boardingSoon"]:
        for direction in route_directions["directions"]:
            # Walking directions can have a [None] routeNumber
            if direction["type"] != "walk" and "routeNumber" is None:
                return False

    return True


# The 'Boarding Soon' section should not contain any walking routes, as they should
# be explicitly within the 'Walking' section.
def no_walking_routes_in_boarding_soon(r):
    response = r.json()
    # Make sure response was successful
    if not response["success"]:
        return False

    # Iterate over directions
    for route_directions in response["data"]["boardingSoon"]:
        if route_directions["numberOfTransfers"] == -1:
            return False

    return True


# We want to ensure that given a query string, /search does not result in an error,
# namely "Cannot read property 'filter' of null," and instead returns a list of
# valid suggestions - autocomplete results that are either of type 'busStop' or 'googlePlace'.
def search_returns_suggestions(r):
    response = r.json()
    # Make sure response was successful
    if not response["success"]:
        return False

    # Iterate over search suggestions
    for suggestion in response["data"]:
        # Check that we do not get the "Cannot filter property null" error
        if "type" not in suggestion or suggestion["type"] not in [
            "googlePlace",
            "busStop",
        ]:
            return False
    return True


def generate_tests(base_url):
    return [
        Test(
            name="Live Tracking 200",
            request=Request(
                method="GET",
                # TODO: Change in future, currently 5000 can only be accessed over http
                url=base_url[:-1].replace("https", "http") + ":5000",
            ),
        ),
        Test(
            name="api/docs 200",
            request=Request(method="GET", url=base_url + "api/docs/"),
        ),
        Test(
            name="api/v1/allstops 200",
            request=Request(method="GET", url=base_url + "api/v1/allstops/"),
        ),
        Test(
            name="api/v2/route 200",
            request=Request(
                method="POST",
                url=base_url + "api/v2/route/",
                payload={
                    "arriveBy": False,
                    "end": "42.454197,-76.440651",
                    "start": "42.449086,-76.483306",
                    "destinationName": 933,
                    "time": time.time(),
                },
            ),
        ),
        Test(
            name="api/v2/route does not contain -1",
            request=Request(
                method="POST",
                url=base_url + "api/v2/route/",
                payload={
                    "arriveBy": False,
                    "end": "42.454197,-76.440651",
                    "start": "42.449086,-76.483306",
                    "destinationName": 933,
                    "time": time.time(),
                },
            ),
            callback=route_number_non_null_callback,
        ),
        Test(
            name="No walking routes in boardingSoon (/api/v2/route)",
            request=Request(
                method="POST",
                url=base_url + "api/v2/route/",
                payload={
                    "arriveBy": False,
                    "end": "42.445228,-76.485053",  # Uris Library
                    "start": "42.440847,-76.483741",  # Collegetown
                    "destinationName": 933,
                    "time": time.time(),
                },
            ),
            callback=no_walking_routes_in_boarding_soon,
        ),
        Test(
            name="api/v1/search contains googlePlaces and busStops",
            request=Request(
                method="POST", 
                url=base_url + "api/v2/search/", 
                payload={"query": "st"}
            ),
            callback=search_returns_suggestions,
        ),
    ]


transit_dev_tests = TestGroup(name="Transit Dev", tests=generate_tests(BASE_DEV_URL))
transit_prod_tests = TestGroup(name="Transit Prod", tests=generate_tests(BASE_PROD_URL))
