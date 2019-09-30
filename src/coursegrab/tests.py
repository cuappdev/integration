from os import environ

from models import Pod, Request, Test, TestGroup

BASE_URL = "https://coursegrab.cornellappdev.com"  # We don't need to mask this since it's public!

tests = [Test(name="Root URL", request=Request(method="GET", url=BASE_URL))]

coursegrab_tests = TestGroup(name="CourseGrab", pod=Pod.COURSEGRAB, tests=tests)
