from datetime import datetime
from os import environ
from subprocess import call
import sys

# Add more test directories here...
from coursegrab import coursegrab_tests
from eatery import eatery_tests
from transit import transit_tests
from uplift import uplift_tests

# And add the test group here as well!
test_groups = [coursegrab_tests, eatery_tests, transit_tests, uplift_tests]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  APPLICATION CODE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SUCCESS_STATUS = 'SUCCESS'
FAILURE_STATUS = 'FAILURE'

num_tests = sum([len(test_group.tests) for test_group in test_groups])
num_failures = 0

slack_message_text = '*Starting new test run...*\n'

for test_group in test_groups:
    slack_message_text += '\tRunning tests for {}...\n'.format(test_group.name)

    test_group_text = ''
    test_group_failures = 0

    for test in test_group.tests:
        test_status = SUCCESS_STATUS # default to printing success

        if not test.is_success():
            test_status = 'FAILURE'
            test_group_failures += 1

        test_group_text += '[{}] - {}\n'.format(test.name, test_status)

    # Only print output if there was more than 0 failures in the group
    if test_group_failures != 0:
        num_failures += test_group_failures
        slack_message_text += "> ```\n{}```\n".format(test_group_text)

if num_failures:
    passed_tests = num_tests - num_failures
    slack_message_text += '\t*Summary: `{}/{}` tests passed!* '.format(passed_tests, num_tests)
else:
    slack_message_text = '*`{0}/{0}` tests passed :white_check_mark:*'.format(num_tests)

if num_failures:
    user_ids = environ['SLACK_USER_IDS']
    slack_message_text += 'cc {}!'.format(user_ids)

# Read output and send to server if necessary
if len(sys.argv) == 2:
    if sys.argv[1] == '--local-only':
        print(slack_message_text)
        exit()
    else:
        print('Unsupported operation, exiting...\n')

CURL_PREFIX = '''curl -X POST -H 'Content-type: application/json' --data '''
CURL_BODY = """'{{ "text": "{}" }}' """.format(slack_message_text)
call(CURL_PREFIX + CURL_BODY + environ['SLACK_HOOK_URL'], shell=True)
