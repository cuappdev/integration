from os import environ, path
from subprocess import call
import sys
import copy

from models import Application, Result, Config

# Add more test directories here...
from coursegrab import coursegrab_tests
from eatery import eatery_tests
from transit import transit_dev_tests, transit_prod_tests
from volume import volume_tests
from uplift import uplift_tests

def run_tests(args=sys.argv[1:]):
    # And add the test group here as well!
    test_groups = [coursegrab_tests, eatery_tests, transit_dev_tests, transit_prod_tests, volume_tests, uplift_tests]
    test_config = None
    default_config = Config.create_default_config(test_groups)
    local_only = False
    locally_run = environ['LOCALLY_RUN'] == 'true'

    if args == []:
        test_config = default_config
    elif args[0] == "--local-only":
        test_config = default_config
        local_only = True
    elif args[0] == "--use-config":
        with open(path.join(environ['BASE_DIR'], 'config/test_config.txt'), 'r') as file:
            j = file.read()
        try:
            test_config = Config(j)
        except Exception as e:
            print(j)
            print(e)
        
        if len(test_config) != len(test_groups):
            test_config = default_config
        # test_config is a json of app names mapped to of "OFF", "ON", or "FAILED"
        # "OFF" represents a disabled test_group
        # "ON" represents an enabled test_group
        # "FAILED" represents a test_group that has failed previously and is will have its output suppressed to prevent spam
        # Config values of "ON" and "FAILED" will be tested
        if "--local-only" in args[1:]:
            local_only = True
    else:
        raise Exception("Invalid args, can use the following: [--use-config] [--local-only]")
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  APPLICATION CODE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    original_config = copy.deepcopy(test_config)

    SUCCESS_STATUS = "SUCCESS"
    FAILURE_STATUS = "FAILURE"

    application_user_id_mapping = {
        Application.EATERY: environ["EATERY_SLACK_USER_IDS"],
        Application.TRANSIT: environ["TRANSIT_SLACK_USER_IDS"],
        Application.VOLUME: environ["VOLUME_SLACK_USER_IDS"],
        Application.UPLIFT: environ["UPLIFT_SLACK_USER_IDS"],

    }
    application_slack_hook_mapping = {
        Application.COURSEGRAB: environ["SLACK_HOOK_COURSEGRAB_URL"],
        Application.EATERY: environ["SLACK_HOOK_EATERY_URL"],
        Application.TRANSIT: environ["SLACK_HOOK_TRANSIT_URL"],
        Application.VOLUME: environ["SLACK_HOOK_VOLUME_URL"],
        Application.UPLIFT: environ["SLACK_HOOK_UPLIFT_URL"],
    }


    for test_group in test_groups:
        if test_config.get(test_group.name) != "OFF":  # Only test enabled or previously failing test groups
            slack_message_text = "\tRunning tests for {}...\n".format(test_group.name)
            test_group_failures = 0
            num_test_group_tests = len(test_group.tests)

            diagnostic_text = ""
            for test in test_group.tests:
                test_status = SUCCESS_STATUS  # default to printing success
                test_result = test.get_result()
                if test_result != Result.SUCCESS:
                    test_group_failures += 1
                    # Mark that there is an error in this pod
                    test_group.slack_message.should_send = True
                diagnostic_text += "[{}] - {}\n".format(test.name, test_result.name)
            slack_message_text += "> ```\n{}```\n".format(diagnostic_text)

            if test_group_failures:
                test_config.set(test_group.name, "FAILED")  # The test group has FAILED at least one test
                passed_tests = num_test_group_tests - test_group_failures
                slack_message_text += "\t*Summary: `{}/{}` tests passed!* ".format(passed_tests, num_test_group_tests)
                # Tag appropriate users
                user_ids = environ["ADMIN_SLACK_USER_IDS"]
                if test_group.application in application_user_id_mapping:
                    user_ids += ", " + application_user_id_mapping[test_group.application]
                slack_message_text += "cc {}!".format(user_ids)
            else:
                test_config.set(test_group.name, "ON")  # The test group has passed, stays ON
                slack_message_text = "*`{0}/{0}` tests passed :white_check_mark:*".format(num_test_group_tests)
            test_group.slack_message.text = slack_message_text
            if locally_run:
                print(test_group.slack_message.text)

    if locally_run:
        f = open(path.join(environ['BASE_DIR'], 'config/test_config.txt'), "w")
        f.write(str(test_config))
        f.close()
    print(test_config)


    # Send output to server if necessary
    if local_only:
        exit()

    CURL_PREFIX = """curl -X POST -H 'Content-type: application/json' --silent --output /dev/null --data """

    for test_group in test_groups:
        if (original_config.get(test_group.name) == "ON" and test_config.get(test_group.name) == "FAILED") or (original_config.get(test_group.name) == "FAILED" and test_config.get(test_group.name) == "ON"):
            # Only output test groups that were passing but newly failed, or were failing but newly passed
            # Suppress output, this behavior can be changed in the future!
            if test_group.slack_message.should_send:
                CURL_BODY = """'{{ "text": "{}" }}' """.format(test_group.slack_message.text)
                call(CURL_PREFIX + CURL_BODY + application_slack_hook_mapping[test_group.application], shell=True)

if __name__ == '__main__':
    run_tests()
