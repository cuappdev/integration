from os import environ
from urllib import parse

from models import Application, Request, Test, TestGroup


BASE_URL = environ["EATERY_BACKEND_URL"]
URL_PARAMS_BASIC = "?query=" + parse.quote("query { eateries { name } }")  # url encoding
URL_PARAMS_CAMPUS_NON_EMPTY = "?query=" + parse.quote(  # url encoding
    """{
  campusEateries {
    about
    name
    nameShort
    coordinates {
      latitude
      longitude
    }
    location
    paymentMethodsEnums
    campusArea{
      descriptionShort
    }
    location
    slug
  }
}
"""
)
URL_PARAMS_COLLEGETOWN_NON_EMPTY = "?query=" + parse.quote(  # url encoding
    """{
  collegetownEateries {
    id
    name
    coordinates {
      latitude
      longitude
    }
    eateryType
    paymentMethodsEnums
    phone
    address
    categories
    price
		ratingEnum
    url
  }
}
"""
)


def all_campus_fields_non_empty(r):
    response = r.json()
    campust_eateries = response["data"]["campusEateries"]
    # Iterate over fields
    for field in campust_eateries:
        if field is None:
            return False
    return True


def all_collegetown_fields_non_empty(r):
    response = r.json()
    campust_eateries = response["data"]["collegetownEateries"]
    # Iterate over fields
    for field in campust_eateries:
        if field is None:
            return False
    return True


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
