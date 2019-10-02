from os import environ
from subprocess import call
import sys
from models import Application, Result

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

application_userID_mapping = {
    Application.EATERY: environ["EATERY_SLACK_USER_IDS"],
    Application.TRANSIT: environ["TRANSIT_SLACK_USER_IDS"],
    Application.UPLIFT: environ["UPLIFT_SLACK_USER_IDS"],
}
application_slack_hook_mapping = {
    Application.COURSEGRAB: environ["SLACK_HOOK_COURSEGRAB_URL"],
    Application.EATERY: environ["SLACK_HOOK_EATERY_URL"],
    Application.TRANSIT: environ["SLACK_HOOK_TRANSIT_URL"],
    Application.UPLIFT: environ["SLACK_HOOK_UPLIFT_URL"],
}

for test_group in test_groups:
    slack_message_text = "\tRunning tests for {}...\n".format(test_group.name)
    test_group_failures = 0
    num_test_group_tests = len(test_group.tests)

    for test in test_group.tests:
        test_status = SUCCESS_STATUS  # default to printing success
        test_result = test.get_result()
        if test_result != Result.SUCCESS:
            test_group_failures += 1
            # Mark that there is an error in this pod
            test_group.slack_message.should_send = True
        slack_message_text += "[{}] - {}\n".format(test.name, test_result.name)

    if test_group_failures:
        passed_tests = num_test_group_tests - test_group_failures
        slack_message_text += "\t*Summary: `{}/{}` tests passed!* ".format(passed_tests, num_test_group_tests)
        # Tag appropriate users
        user_ids = environ["ADMIN_SLACK_USER_IDS"]
        if test_group.application in application_userID_mapping:
            user_ids += ", " + application_userID_mapping[test_group.application]
        slack_message_text += "cc {}!".format(user_ids)
    else:
        slack_message_text = "*`{0}/{0}` tests passed :white_check_mark:*".format(num_test_group_tests)
    test_group.slack_message.text = slack_message_text

    # Always print output for debugging purposes
    print(test_group.slack_message.text)

# Send output to server if necessary
if len(sys.argv) == 2:
    if sys.argv[1] == "--local-only":
        exit()
    else:
        print("Unsupported operation, exiting...\n")

CURL_PREFIX = """curl -X POST -H 'Content-type: application/json' --data """
for test_group in test_groups:
    # Suppress output, this behavior can be changed in the future!
    if test_group.slack_message.should_send:
        CURL_BODY = """'{{ "text": "{}" }}' """.format(test_group.slack_message.text)
        call(CURL_PREFIX + CURL_BODY + application_slack_hook_mapping[test_group.application], shell=True)
