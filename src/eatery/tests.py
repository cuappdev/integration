from os import environ
from urllib import parse

from models import Application, Request, Test, TestGroup


BASE_URL = environ["EATERY_BACKEND_URL"]
URL_PARAMS_BASIC = "?query=" + parse.quote("query { eateries { name } }")  # url encoding
URL_PARAMS_CAMPUS_NON_EMPTY = "?query=" + parse.quote(  # url encoding
    """{
  campusEateries {
    about
    campusArea {
      descriptionShort
    }
    coordinates {
      latitude
      longitude
    }
    location
    name
    nameShort
    paymentMethodsEnums
    slug
  }
}
"""
)
URL_PARAMS_COLLEGETOWN_NON_EMPTY = "?query=" + parse.quote(  # url encoding
    """{
  collegetownEateries {
    address
    categories
    coordinates {
      latitude
      longitude
    }
    eateryType
    id
    name
    paymentMethodsEnums
    phone
    price
    ratingEnum
    url
  }
}
"""
)


def all_campus_fields_non_empty(r):
    response = r.json()
    return all(response["data"]["campusEateries"])


def all_collegetown_fields_non_empty(r):
    response = r.json()
    return all(response["data"]["collegetownEateries"])


tests = [
    Test(name="Eateries on campus query", request=Request(method="GET", url=BASE_URL + URL_PARAMS_BASIC)),
    Test(
        name="Fields that should never be empty for campus eateries query",
        request=Request(method="GET", url=BASE_URL + URL_PARAMS_CAMPUS_NON_EMPTY),
        callback=all_campus_fields_non_empty,
    ),
    Test(
        name="Fields that should never be empty for collegetown eateries query",
        request=Request(method="GET", url=BASE_URL + URL_PARAMS_COLLEGETOWN_NON_EMPTY),
        callback=all_collegetown_fields_non_empty,
    ),
]

eatery_tests = TestGroup(application=Application.EATERY, name="Eatery", tests=tests)
