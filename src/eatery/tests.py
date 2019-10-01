from os import environ
from urllib import parse

from models import Application, Request, Test, TestGroup

BASE_URL = environ["EATERY_BACKEND_URL"]
URL_PARAMS = "?query=" + parse.quote("query { eateries { name } }")  # url encoding

tests = [Test(name="Eateries on Campus query", request=Request(method="GET", url=BASE_URL + URL_PARAMS))]

eatery_tests = TestGroup(application=Application.EATERY, name="Eatery", tests=tests)
