# serverless-copy
AWS Lambda Function to copy files from S3 to Oracle Cloud Infrastructure Bucket using a Serverless method

This code is a AWS Lambda function that copies files from an AWS S3 bucket to an Oracle Cloud Infrastructure (OCI) Object Storage bucket. The code uses the boto3 library, which is the Amazon Web Services (AWS) SDK for Python, to interact with the AWS and OCI object storage services.

The function starts by reading the values of various parameters from the event argument:

    file_extension: The file extension of the files to be copied.
    days: The maximum age of the files to be copied. Only files that were created or modified within the last days number of days will be copied.
    aws_bucket: The name of the AWS S3 bucket to copy the files from.
    oracle_bucket: The name of the OCI Object Storage bucket to copy the files to.
    oracle_endpoint_url: The endpoint URL for the OCI Object Storage service.
    oracle_region: The region for the OCI Object Storage service.
    oracle_access_key_id: The access key ID for the OCI Object Storage service.
    oracle_secret_access_key: The secret access key for the OCI Object Storage service.
    sns_topic_arn: The Amazon Resource Name (ARN) of an Amazon Simple Notification Service (SNS) topic.
    dynamodb_table_name: The name of a DynamoDB table.

Next, the code creates an AWS S3 client using the boto3.client method and lists all the objects in the specified AWS S3 bucket using the list_objects method. The code then gets the timestamp to filter the files and filters the files based on their file extension and the modified time being older than the specified number of days.

The code then creates an OCI Object Storage client using the boto3.client method and a DynamoDB client using the same method. If the specified DynamoDB table does not exist, the code creates the table using the create_table method.

Finally, the code iterates through the filtered files and tries to copy each file to the OCI Object Storage bucket. If an error occurs during the copy operation, the code publishes an error message to the specified SNS topic and adds information about the file and the status of the copy operation to the DynamoDB table. If the copy operation is successful, the code adds information about the file and the status of the copy operation to the DynamoDB table.

Overall, this code implements a solution for copying files from an AWS S3 bucket to an OCI Object Storage bucket, with error handling and logging capabilities.
