"""Lambda Function that kicks off with an AWS CloudWatch Tag event
   to add/delete subscription filter on a CloudWatch log group."""

import os
import boto3

# initiate boto3 logs client
SESSION = boto3.session.Session()
LOGS_CLIENT = SESSION.client('logs')

# retrieve environment variables
SUB_PATTERN = ""
SUB_NAME = str(os.getenv('SUB_FILTER_NAME'))
SUB_DEST_ARN = str(os.getenv('SUB_DEST_ARN'))
SUB_ROLE_ARN = str(os.getenv('SUB_ROLE_ARN'))
TAG_KEY = str(os.getenv('TAG_KEY'))
TAG_VALUE = str(os.getenv('TAG_VALUE'))

def get_resource_type(event):
    """Return the resource type of an event."""
    raw_cloudwatch_msg = event
    resource_type = raw_cloudwatch_msg['detail']['resource-type']
    return resource_type

def get_lg_name(event):
    """Return the name of a log group."""
    raw_cloudwatch_msg = event
    log_group_arn = raw_cloudwatch_msg['resources'][0]
    lg_name = log_group_arn.split("log-group:", 1)[1]
    return lg_name

def get_log_group_tags(event):
    """Return the tags of a log group."""
    raw_cloudwatch_msg = event
    log_group_tags = raw_cloudwatch_msg['detail']['tags']
    return log_group_tags

def get_sub(lg_name, subscription_filter_name):
    """Return the subscription of a log group."""
    response = LOGS_CLIENT.describe_subscription_filters(
        logGroupName=lg_name,
        filterNamePrefix=subscription_filter_name,
        limit=1
    )
    return response


def lambda_handler(event, __):
    """Tag event to add/delete subscription filter on log group."""

    print("Beginning Lambda Execution...")

    # check to see if event resource type is log-group
    if get_resource_type(event) == 'log-group':

        lg_name = get_lg_name(event)
        tags = get_log_group_tags(event)

        # check to see if there is a tag match
        if TAG_KEY in tags.keys():

            tag_value_found = str(tags[TAG_KEY]).lower()

            # tag match found. determine if key value is correct
            if tag_value_found == TAG_VALUE:
                # put sub filter on the log group.
                response = LOGS_CLIENT.put_subscription_filter(
                    logGroupName=lg_name,
                    filterName=SUB_NAME,
                    filterPattern=SUB_PATTERN,
                    destinationArn=SUB_DEST_ARN,
                    distribution='Random'
                )

                print("Put Subscription Filter Response: "
                      + str(response))

                # check to see if sub filter successfully added
                # and destination is correct
                sub = get_sub(lg_name, SUB_NAME)['subscriptionFilters'][0]
                dest_arn = sub['destinationArn']
                if dest_arn == SUB_DEST_ARN:
                    print("success. cloudwatch log group [" + lg_name + "]"
                          " is routed to destination: "+SUB_DEST_ARN)


            # if tag is not true, we want to remove the subscription filter
            else:
                if len(get_sub(lg_name, SUB_NAME)['subscriptionFilters']) != 0:
                    response = LOGS_CLIENT.delete_subscription_filter(
                        logGroupName=lg_name,
                        filterName=SUB_NAME
                    )

                    print("Delete Subscription Filter Response: "
                          + str(response))

                    print("success. cloudwatch log group [" + lg_name + "]"
                          " is no longer routed to destination: "
                          +SUB_DEST_ARN)
                else:
                    print("cloudwatch log group [" + lg_name + "]"
                          " has no subscription filter / destination.")
        else:
            print("failed. tag key not found.")
    else:
        print("failed. resource-type was not log-group.")

    print("Ending Lambda Execution...")
