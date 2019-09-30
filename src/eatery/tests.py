from os import environ

from models import Pod, Request, Test, TestGroup

BASE_URL = environ["EATERY_BACKEND_URL"]
URL_PARAMS = "?query=query%7Beateries%20%7Bname%7D%7D"

tests = [Test(name="Eateries on Campus query", request=Request(method="GET", url=BASE_URL + URL_PARAMS))]

eatery_tests = TestGroup(name="Eatery", tests=tests, pod=Pod.EATERY)
