from os import environ
from subprocess import call
import sys
from models import Application, Result

# Add more test directories here...
from coursegrab import coursegrab_tests 
from eatery import eatery_tests 
from transit import transit_dev_tests, transit_prod_tests
from volume import volume_tests

test_groups = [volume_tests]
test_config = []
local_only = False 
default_config=[]
# And add the test group here as well!
try:
    f = open("test_config.txt", "r")
    default_config = list(f.read())
    if(len(default_config)!=len(test_groups)):
        raise Exception("Invalid config length, length is currently "+ str(len(default_config))+", should be length: "+ str(len(test_groups)))
except Exception as e:
    print(e)
    default_config=["1"]*len(test_groups)

match sys.argv[1:]:
    case []:
        test_config = default_config
    case ["--local-only"]: 
        test_config = default_config
        local_only=True
    case ["--tests", tc, *args]:
        test_config = list(tc)
        if(len(test_config)!=len(test_groups)):
            raise Exception("Invalid config length, length is currently "+ str(len(test_config))+", should be length: "+ str(len(test_groups)))
        # test_config is a list of 0s, 1s, or 2s that have a 1:1 mapping to test_groups_default
        # 0 represents a disabled test_group
        # 1 represents an enabled test_group
        # 2 represents a test_group that has failed previously and is will have its output suppressed to prevent spam
        # Config values of 1 and 2 will be tested
        if "--local-only" in args:
            local_only=True
    case _:
        raise Exception("Invalid args, should be: [--tests <test_config>] [--local-only]")
copy_config = test_config[:]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  APPLICATION CODE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SUCCESS_STATUS = "SUCCESS"
FAILURE_STATUS = "FAILURE"

application_user_id_mapping = {
    Application.EATERY: environ["EATERY_SLACK_USER_IDS"],
    Application.TRANSIT: environ["TRANSIT_SLACK_USER_IDS"],
    Application.VOLUME: environ["VOLUME_SLACK_USER_IDS"],
}
application_slack_hook_mapping = {
    Application.COURSEGRAB: environ["SLACK_HOOK_COURSEGRAB_URL"],
    Application.EATERY: environ["SLACK_HOOK_EATERY_URL"],
    Application.TRANSIT: environ["SLACK_HOOK_TRANSIT_URL"],
    Application.VOLUME: environ["SLACK_HOOK_VOLUME_URL"],
}


for i in range(len(test_groups)):
    if test_config[i]!="0":  # Only test enabled or previously failing test groups
        test_group=test_groups[i]
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
            test_config[i]="2" # The test group has failed
            passed_tests = num_test_group_tests - test_group_failures
            slack_message_text += "\t*Summary: `{}/{}` tests passed!* ".format(passed_tests, num_test_group_tests)
            # Tag appropriate users
            user_ids = environ["ADMIN_SLACK_USER_IDS"]
            if test_group.application in application_user_id_mapping:
                user_ids += ", " + application_user_id_mapping[test_group.application]
            slack_message_text += "cc {}!".format(user_ids)
        else:
            test_config[i]="1" # The test group has passed
            slack_message_text = "*`{0}/{0}` tests passed :white_check_mark:*".format(num_test_group_tests)
        test_group.slack_message.text = slack_message_text
        # Always print output for debugging purposes
        print(test_group.slack_message.text)

print(test_config)

f = open("./test_config.txt", "w")
f.write("".join(test_config))
f.close()


# Send output to server if necessary
if local_only:
    exit()

CURL_PREFIX = """curl -X POST -H 'Content-type: application/json' --data """
for i in range(len(test_groups)):
    if copy_config[i]=="1" or test_config[i]=="1": # Only output enabled test groups, which include newly failing ones
        test_group=test_groups[i]
        # Suppress output, this behavior can be changed in the future!
        if test_group.slack_message.should_send:
            CURL_BODY = """'{{ "text": "{}" }}' """.format(test_group.slack_message.text)
            call(CURL_PREFIX + CURL_BODY + application_slack_hook_mapping[test_group.application], shell=True)



