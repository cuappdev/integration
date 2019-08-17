from models import Test, TestGroup

tests = [
    Test(
        name='Eateries on Campus query',
        url='http://eatery-backend.cornellappdev.com/?query=query%7B%0Aeateries%20%7Bname%7D%7D',
    ),
]

eatery_tests = TestGroup(name='Eatery', tests=tests)
