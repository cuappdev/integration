from os import environ

from models import Request, Test, TestGroup, Pod

BASE_URL = environ["EATERY_BACKEND_URL"]

tests = [
    Test(
        name="Eateries on Campus query",
        request=Request(
            method="GET", url=BASE_URL + "?query=query%7Beateries%20%7Bname%7D%7D"
        ),
    )
]

eatery_tests = TestGroup(name="Eatery", tests=tests, pod=Pod.EATERY)
