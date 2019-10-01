from models import Application, Request, Test, TestGroup

BASE_URL = "https://coursegrab.cornellappdev.com"  # We don't need to mask this since it's public!

tests = [Test(name="Root URL", request=Request(method="GET", url=BASE_URL))]

coursegrab_tests = TestGroup(application=Application.COURSEGRAB, name="CourseGrab", tests=tests)
