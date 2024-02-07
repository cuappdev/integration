from os import environ
from urllib import parse

from models import Application, Request, Test, TestGroup


BASE_URL = environ["EATERY_BACKEND_URL"]
SIMPLE_EATERY_QUERY = "eatery/simple/"
EATERY_QUERY_BY_ID = "eatery/5/"
FULL_EATERY_QUERY = "eatery/"

tests = [
    Test(name="Simple eateries query", request=Request(method="GET", url=BASE_URL + SIMPLE_EATERY_QUERY)),
    Test(
        name="Get eatery by id",
        request=Request(method="GET", url=BASE_URL + EATERY_QUERY_BY_ID)
    ),
    Test(
        name="Get all eatery data",
        request=Request(method="GET", url=BASE_URL + FULL_EATERY_QUERY),
    ),
]

eatery_tests = TestGroup(application=Application.EATERY, name="Eatery", tests=tests)
