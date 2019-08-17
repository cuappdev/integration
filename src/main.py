from os import environ
from subprocess import call

# Add more test directories here...
from eatery import eatery_tests
from transit import transit_tests

# And add the test group here as well!
test_groups = [eatery_tests, transit_tests]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  APPLICATION CODE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SUCCESS_STATUS = 'SUCCESS'
FAILURE_STATUS = 'FAILURE'

num_tests = [len(test_group.tests) for test_group in test_groups]
num_failures = 0

slack_message_text = ''

for test_group in test_groups:
    slack_message_text += 'Running tests for {}...\n'.format(test_group.name)

    test_group_curl_body = ''
    test_group_failures = 0

    for test in test_group.tests:
        test_status = SUCCESS_STATUS # default to printing success

        if not test.is_success():
            test_status = 'FAILURE'
            test_group_failures += 1

        slack_message_text += '[{}] - {}\n'.format(test.name, test_status)

    # Only print output if there was more than 0 failures in the group
    if test_group_failures != 0:
        num_failures += test_group_failures
        slack_message_text += "```\n{}```\n".format(test_group_curl_body)

# We finished running all tests, finish formatting and send the output to Slack!
slack_message_text += '*Summary: {}/{} tests passed!*'.format(num_tests - num_failures, num_tests)

CURL_PREFIX = '''curl -X POST -H 'Content-type: application/json' --data '''
CURL_BODY = """'{{ "text": "{}" }}' """.format(slack_message_text)
call(CURL_PREFIX + CURL_BODY + environ['SLACK_HOOK_URL'], shell=True)
