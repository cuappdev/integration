from os import environ
from urllib import parse

from models import Application, Request, Test, TestGroup


BASE_URL = environ["EATERY_BACKEND_URL"]
SIMPLE_EATERY_QUERY = "eatery/simple/"
EATERY_QUERY_BY_ID = "eatery/5/"

tests = [
    Test(name="Simple eateries query", request=Request(method="GET", url=BASE_URL + SIMPLE_EATERY_QUERY)),
    Test(
        name="Get eatery by id",
        request=Request(method="GET", url=BASE_URL + EATERY_QUERY_BY_ID)
    ),
]

eatery_tests = TestGroup(application=Application.EATERY, name="Eatery", tests=tests)
