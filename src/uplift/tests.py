from os import environ
from urllib import parse

from models import Application, Request, Test, TestGroup

BASE_URL = environ["UPLIFT_BACKEND_URL"]
URL_PARAMS_BASIC = "?query=" + parse.quote("query { gyms { name } }")  # url encoding
URL_PARAMS_GYMS_NON_EMPTY = "?query=" + parse.quote(  # url encoding
    """
    query GymsQuery {
        gyms {
          address
          imageUrl
          latitude
          longitude
          name
          facilities {
              name
              facilityType
              capacity{
                count
                percent
                updated
              }
              hours{
                courtType
                startTime
                endTime
                isShallow
                isShallow
                isWomen
              }
          }
          hours{
                courtType
                startTime
                endTime
                isShallow
                isShallow
                isWomen
              }
        }
    }
    """
)
URL_PARAMS_CLASSES_NON_EMPTY = "?query=" + parse.quote(  # url encoding
    """
    query ClassesInfoQuery {
        classes {
            date
            endTime
            isCancelled
            startTime
        }
    }
        """
)


def all_gym_fields_non_empty(r):
    response = r.json()
    return all(response["data"]["gyms"])


def all_classes_fields_non_empty(r):
    response = r.json()
    return all(response["data"]["classes"])


tests = [
    Test(name="Gyms on Campus query", request=Request(method="GET", url=BASE_URL + URL_PARAMS_BASIC)),
    Test(
        name="Fields that should never be empty for gyms query",
        request=Request(method="GET", url=BASE_URL + URL_PARAMS_GYMS_NON_EMPTY),
        callback=all_gym_fields_non_empty,
    ),
    # Test(
    #     name="Fields that should never be empty for classes info query",
    #     request=Request(method="GET", url=BASE_URL + URL_PARAMS_CLASSES_NON_EMPTY),
    #     callback=all_classes_fields_non_empty,
    # ),

    # There doesn't seem to be classes on the api atm
]

uplift_tests = TestGroup(application=Application.UPLIFT, name="Uplift", tests=tests)
