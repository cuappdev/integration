from os import environ

from models import Pod, Request, Test, TestGroup

BASE_URL = environ["UPLIFT_BACKEND_URL"]
URL_PARAMS = "?query=query%7B%0Agyms%7B%0Aname%0A%7D%0A%7D"

tests = [Test(name="Gyms on Campus query", request=Request(method="GET", url=BASE_URL + URL_PARAMS))]

uplift_tests = TestGroup(name="Uplift", tests=tests, pod=Pod.UPLIFT)
