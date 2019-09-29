from datetime import datetime
from os import environ
from subprocess import call
import sys
from models import Result, Pod

# Add more test directories here...
from coursegrab import coursegrab_tests
from eatery import eatery_tests
from transit import transit_dev_tests, transit_prod_tests
from uplift import uplift_tests

# And add the test group here as well!
test_groups = [coursegrab_tests, eatery_tests, transit_dev_tests, transit_prod_tests, uplift_tests]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  APPLICATION CODE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SUCCESS_STATUS = "SUCCESS"
FAILURE_STATUS = "FAILURE"

num_tests = sum([len(test_group.tests) for test_group in test_groups])
num_failures = 0
pod_error_tracking = {Pod.EATERY: False, Pod.TRANSIT: False, Pod.UPLIFT: False}

slack_message_text = "*Starting new test run...*\n"

for test_group in test_groups:
    slack_message_text += "\tRunning tests for {}...\n".format(test_group.name)

    test_group_text = ""
    test_group_failures = 0

    for test in test_group.tests:
        test_status = SUCCESS_STATUS  # default to printing success

        test_result = test.get_result()
        if test_result != Result.SUCCESS:
            test_group_failures += 1
            # Mark that there is an error in this pod
            pod_error_tracking[test_group.pod] = True
        test_group_text += "[{}] - {}\n".format(test.name, test_result.name)

    # Only print output if there was more than 0 failures in the group
    if test_group_failures != 0:
        num_failures += test_group_failures
        slack_message_text += "> ```\n{}```\n".format(test_group_text)

if num_failures:
    passed_tests = num_tests - num_failures
    slack_message_text += "\t*Summary: `{}/{}` tests passed!* ".format(passed_tests, num_tests)
    # Tag appropriate users
    user_ids = environ["MAIN_SLACK_USER_IDS"]
    if pod_error_tracking[Pod.EATERY]:
        user_ids += ", " + environ["EATERY_SLACK_USER_IDS"]
    if pod_error_tracking[Pod.TRANSIT]:
        user_ids += ", " + environ["TRANSIT_SLACK_USER_IDS"]
    if pod_error_tracking[Pod.UPLIFT]:
        user_ids += ", " + environ["UPLIFT_SLACK_USER_IDS"]
    slack_message_text += "cc {}!".format(user_ids)
else:
    slack_message_text = "*`{0}/{0}` tests passed :white_check_mark:*".format(num_tests)

# Always print output for debugging purposes
print(slack_message_text)

# Send output to server if necessary
if len(sys.argv) == 2:
    if sys.argv[1] == "--local-only":
        exit()
    else:
        print("Unsupported operation, exiting...\n")

if num_failures:
    # Suppress output, this behavior can be changed in the future!
    CURL_PREFIX = """curl -X POST -H 'Content-type: application/json' --data """
    CURL_BODY = """'{{ "text": "{}" }}' """.format(slack_message_text)
    call(CURL_PREFIX + CURL_BODY + environ["SLACK_HOOK_URL"], shell=True)
