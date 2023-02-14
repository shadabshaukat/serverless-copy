import boto3
import os
import datetime

def lambda_handler(event, context):
    # Get the file extension to be copied
    file_extension = event['extension']
    days = event['days']
    aws_bucket = event['aws_bucket']
    oracle_bucket = event['oracle_bucket']
    oracle_endpoint_url = event['oracle_endpoint_url']
    oracle_region = event['oracle_region']
    oracle_access_key_id = event['oracle_access_key_id']
    oracle_secret_access_key = event['oracle_secret_access_key']
    sns_topic_arn = event['sns_topic_arn']
    dynamodb_table_name = event['dynamodb_table_name']
    
    # Create S3 client for AWS S3
    s3_aws = boto3.client('s3')

    # List all objects in the AWS S3 bucket
    result = s3_aws.list_objects(Bucket=aws_bucket)

    # Get all the files in the AWS S3 bucket
    files = result.get("Contents")

    # Get the timestamp to filter files. 'days' is the age filter and it only copies the files which are younger than the value specificied. It will only copy the files which have created/changed in the last 100 days
    timestamp = datetime.datetime.now() - datetime.timedelta(days=days)

    # Filter the files with the desired file extension and modified time older than the timestamp
    filtered_files = [file for file in files if file['Key'].endswith(file_extension) and 
                      datetime.datetime.strptime(file['LastModified'].strftime('%Y-%m-%d %H:%M:%S'), 
                      '%Y-%m-%d %H:%M:%S') > timestamp]

    # Create S3 client for OCI object storage
    s3_oci = boto3.client('s3',
                      endpoint_url=oracle_endpoint_url,
                      region_name=oracle_region,
                      aws_access_key_id=oracle_access_key_id,
                      aws_secret_access_key=oracle_secret_access_key)

    # Create a DynamoDB client
    dynamodb = boto3.client('dynamodb')
    
    # Create the DynamoDB table if it does not exist
    try:
        dynamodb.describe_table(TableName=dynamodb_table_name)
    except dynamodb.exceptions.ResourceNotFoundException:
        dynamodb.create_table(
            TableName=dynamodb_table_name,
            KeySchema=[
                {
                    'AttributeName': 'file_name',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'file_name',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

    # Copy each file with the desired file extension to the OCI bucket
    for file in filtered_files:
        try:
            obj = s3_aws.get_object(Bucket=aws_bucket, Key=file['Key'])
            data = obj['Body'].read()
            # Replicate the AWS S3 bucket folder structure to the OCI bucket
            folder_structure = os.path.dirname(file['Key'])
            oci_key = folder_structure + '/' + os.path.basename(file['Key'])
            s3_oci.put_object(Bucket=oracle_bucket, Key=oci_key, Body=data)
            #s3_oci.put_object(Bucket=oracle_bucket, Key=os.path.basename(file['Key']), Body=data)
            # Add the copied file to the DynamoDB table
            dynamodb.put_item(TableName=dynamodb_table_name, Item={'file_name': {'S': os.path.basename(file['Key'])}})
        except Exception as e:
            # Publish the error to the SNS topic
            sns = boto3.client('sns')
            sns.publish(TopicArn=sns_topic_arn, Message='Error copying file : ' + file['Key'] + ' to Bucket : ' + oracle_bucket)
