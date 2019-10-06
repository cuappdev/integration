from os import environ
from urllib import parse

from models import Application, Request, Test, TestGroup

BASE_URL = environ["EATERY_BACKEND_URL"]
URL_PARAMS1 = "?query=" + parse.quote("query { eateries { name } }")  # url encoding
URL_PARAMS2 = "?query=" + parse.quote(
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


# We want to verify that /allstops returns a list of type 'busStop' only
def All_Fields_Non_Empty(r):
    response = r.json()
    # Iterate over stops
    campust_eateries = response["data"]["campusEateries"]
    for field in campust_eateries:
        if not (field is None):
            return False
    return True


tests = [
    Test(name="Eateries on campus query", request=Request(method="GET", url=BASE_URL + URL_PARAMS1)),
    Test(
        name="Fields that should never be empty query",
        request=Request(method="GET", url=BASE_URL + URL_PARAMS2),
        callback=All_Fields_Non_Empty,
    ),
]

eatery_tests = TestGroup(application=Application.EATERY, name="Eatery", tests=tests)
