from models import Test, TestGroup

tests = [
    Test(
        name='Transit Docs 200',
        url='http://transit-backend.cornellappdev.com/api/docs/',
    ),
    Test(
        name='Transit AllStops 200',
        url='http://transit-backend.cornellappdev.com/api/v1/allstops/',
    ),
]

transit_tests = TestGroup(name='Transit', tests=tests)
