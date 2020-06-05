# cross-account-cwlog-routing

## Automated, Cross-Account CloudWatch Log Routing

Proof of Concept to show how CloudWatch Event Rules + Lambda can route cloudwatch logs from one/many account(s) to a central logging account.

## About

Some CloudWatch logs are more important than others.  You'll want to route these logs to destinations like Redshift or Splunk to get the most insight and value out of your logs.  To do this automatically, we can utilize cloudwatch event rules to route cloudwatch log groups any time a specific tag is added.  This solution takes a multi-account approach with many log "sender" accounts, and one log "receiver" account.

----

## Architecture

![Stack-Resources](architecture/cwl_routing.png)

----

## Prerequisites

1. At least 2 AWS accounts. 1 sender and 1 receiver.
2. An S3 Bucket in each account for Lambda Code Artifacts.
3. A KMS key to encrypt your Kinesis Stream, Kinesis Firehose, and S3 Bucket

## Before you deploy

1. In the receiver AWS account, place receiver/scripts/log_processor.zip in an s3 bucket for cloudformation to reference when deploying a lambda function. Take note of the bucket name and account ID
2. In the sender AWS account(s), place sender/scripts/cwl_routing.zip in an s3 bucket for cloudformation to reference when deploying a lambda function. Take note of the bucket name and account ID

----

## Log Receiver Account - Deploying Cloudformation

1. Log in to the AWS account that you'd like to receive and store CloudWatch Logs in.
2. Go to [AWS Cloudformation Console](https://console.aws.amazon.com/cloudformation/) and choose **Create stack**
3. upload the receiver/receiver.yaml template
4. enter parameters

This Stack will create the following:

1. S3 bucket (storage of cloudwatch logs from all accounts)
2. CloudWatch Logs Destination (encapsulates a physical resource (such as an Amazon Kinesis data stream))
3. Kinesis Stream (receives logs from all accounts)
4. Kinesis Firehose Delivery Stream (takes records from kinesis stream, processes them, and sends to S3 bucket)
5. Lambda Function to process records in Kinesis Firehose
6. IAM roles/policies for Lambda, Kinesis, etc.

## Log Receiver Account - Manually Add KMS Encryption to Kinesis Stream

Why manually?

When deploying a Logs Destination, Cloudformation will send a test record to ensure it reaches its destination.  I've come across errors where a KMS-Encrypted Kinesis Stream resource will cause this test to fail. To mitigate this issue, I've removed this from the cloudformation Kinesis resource:

                StreamEncryption:
                        EncryptionType: KMS
                        KeyId: !Ref pKMSKeyId

Instead, [add KMS Encryption Manually.](https://docs.aws.amazon.com/streams/latest/dev/getting-started-with-sse.html)

## Log Sender Account(s) - Deploying Cloudformation

1. Log in to an AWS account that you'd like send CloudWatch Logs from
2. Go to [AWS Cloudformation Console](https://console.aws.amazon.com/cloudformation/) and choose **Create stack**
3. upload the sender/sender.yaml template
4. enter parameters

This Stack will create the following:

1. CloudWatch Events Rule (Add Tag to Log Group)
2. Lambda Function to Put Subscription Filter on a Log Group

----

## Utilizing the Solution

### Log Sender Account(s) - Add a tag to a cloudwatch log group

The solution is designed to automatically route cloudwatch logs if a log group is given a specific tag. (ex. captured: true)

#### Tag Basics

You use the AWS CLI or CloudWatch Logs API as a user in your Log Sender Account to complete the following tasks:

- Add tags to a log group when you create it
- Add tags to an existing log group
- List the tags for a log group
- Remove tags from a log group

You can use tags to categorize your log groups. For example, you can categorize them by purpose, owner, or environment. Because you define the key and value for each tag, you can create a custom set of categories to meet your specific needs. For example, you might define a set of tags that helps you track log groups by owner and associated application. Here are several examples of tags:

- Project: Project name
- Owner: Name
- Purpose: Load testing
- Application: Application name
- Environment: Production

via [Working with Log Groups and Log Streams](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/Working-with-log-groups-and-streams.html#log-group-tagging)

CLI Example:

        aws logs tag-log-group --log-group-name /aws-glue/crawlers --tags captured=true

### Check to see if subscription filter was added to cloudwatch log group

1. Go to [CloudWatch Log groups Console](https://console.aws.amazon.com/cloudwatch/home#logs:)
2. Your Log Group should now have a subscription under the **Subscriptions** column.

----

### Log Receiver Account - See logs routed to Kinesis Stream, Kinesis Firehose delivery stream, and finally, S3

Once the log groups in your sender accounts generate logs, they will automatically be sent to the Kinesis Stream in the receiver account.

1. Log in to the AWS account that you'd like to receive and store CloudWatch Logs in.
2. Use the [Kinesis Console](https://console.aws.amazon.com/kinesis/home) to select the newly created Kinesis Stream and/or Firehose delivery stream.
3. Select Monitoring tab to view events on each stream.
4. Go to the [S3 Console](https://s3.console.aws.amazon.com/s3/home) and select the newly created S3 bucket. Logs should be delivered there.
