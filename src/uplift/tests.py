from os import environ
from urllib import parse

from models import Application, Request, Test, TestGroup

BASE_URL = environ["UPLIFT_BACKEND_URL"]
URL_PARAMS = "?query=" + parse.quote("query { gyms { name } }")  # url encoding

tests = [Test(name="Gyms on Campus query", request=Request(method="GET", url=BASE_URL + URL_PARAMS))]

uplift_tests = TestGroup(application=Application.UPLIFT, name="Uplift", tests=tests)
