import time
from os import environ

from datetime import datetime
from models import Application, Request, Test, TestGroup

BASE_DEV_URL = environ["TRANSIT_DEV_BACKEND_URL"]
BASE_PROD_URL = environ["TRANSIT_BACKEND_URL"]

GTFS_EXPIRATION_BUFFER = 7  # number of days before GTFS feed expiration date

# We want to verify that /allstops returns a list of type 'busStop' only
def allstops_returns_bus_stops(r):
    response = r.json()
    # Make sure response was successful
    if not response["success"]:
        return False

    # Iterate over stops
    for stop in response["data"]:
        # Check that the BusStop object is properly decoded
        if "type" not in stop or stop["type"] != "busStop":
            return False
    return True


# There should always be at least one walking route displayed to the user
def at_least_one_walking_route(r):
    response = r.json()
    # Make sure response was successful
    if not response["success"]:
        return False

    # Verify list of walking directions is not empty
    walking_directions = response["data"]["walking"]
    return walking_directions is not None or len(walking_directions) > 0


def check_gtfs_feed_expiration(r):
    response = r.json()
    # Make sure response was successful
    if not response["success"]:
        return False

    end_date = datetime.strptime(response["data"]["feed_end_date"], "%Y%m%d")
    today = datetime.today()

    if today < end_date:
        return (end_date - today).days > GTFS_EXPIRATION_BUFFER

    return False


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
            if direction["type"] != "walk" and direction["routeNumber"] is None:
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
# valid suggestions - autocomplete results that are either of type 'applePlace' or 'busStop'.
def search_returns_suggestions(r):
    response = r.json()
    # Make sure response was successful
    if not response["success"]:
        print("not successful")
        return False

    # Iterate over two types of search suggestions
    for suggestion in response["data"]:
        if suggestion not in ["applePlaces", "busStops"]:
            return False
            for busStop in suggestion["busStops"]:
                if not busStop.get("type") == "busStop":
                    return False
            for applePlace in suggestion["applePlaces"]:
                if not applePlace.get("type") == "applePlace":
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
        Test(name="api/docs 200", request=Request(method="GET", url=base_url + "api/docs/")),
        Test(name="api/v1/allstops 200", request=Request(method="GET", url=base_url + "api/v1/allstops/")),
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
            name="api/v2/appleSearch contains applePlaces and busStops",
            request=Request(method="POST", url=base_url + "api/v2/appleSearch", payload={"query": "st"}),
            callback=search_returns_suggestions,
        ),
        Test(
            name="api/v1/allstops only contains busStops",
            request=Request(method="GET", url=base_url + "api/v1/allstops/"),
            callback=allstops_returns_bus_stops,
        ),
        Test(
            name="At least one walking route shown (/api/v2/route)",
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
            callback=at_least_one_walking_route,
        ),
    ]


transit_dev_tests = TestGroup(application=Application.TRANSIT, name="Transit Dev", tests=generate_tests(BASE_DEV_URL))
transit_prod_tests = TestGroup(
    application=Application.TRANSIT, name="Transit Prod", tests=generate_tests(BASE_PROD_URL)
)
