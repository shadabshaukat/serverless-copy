# Serverless-Copy-S3-to-OCI

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

## Deploy

#### 1. Clone the code from Github
```
$ git clone https://github.com/shadabshaukat/serverless-copy-aws-to-oci.git
```

#### 2.  Switch to the code directory
```
$ cd serverless-copy-aws-to-oci/
```

#### 3.  Configure your AWS cli credentials after creating access key for your user
```
$ aws configure

AWS Access Key ID [None]: ********
AWS Secret Access Key [None]: *******
Default region name [None]: ap-southeast-2
Default output format [None]:
```

#### 4. Zip the Lambda function code
```
$ zip -r lambda.zip *
```

#### 5. Upload to your S3 bucket
```
$ aws s3 cp lambda.zip s3://<your s3 bucket>/
```

#### 6.  Create the Python3.9 AWS Lambda Function
```
$ aws lambda create-function --function-name s3-to-oci --runtime python3.9 --role <your role arn> --handler lambda_function.lambda_handler --code S3Bucket=<your s3 bucket>,S3Key=lambda.zip
```

#### 7.  Modify the Lambda Fn timeout (in seconds, 900s is 15mins)
```
$ aws lambda update-function-configuration --function-name s3-to-oci --timeout 900
```

#### 8.  Create event.json file to store the arguements for your environment. Replace the values in the event JSON file with your own values.
```
$ vim event.json 

{
  "extension": ".txt",
  "days": 1000,
  "aws_bucket": "sourceaws-serverless-copy",
  "oracle_bucket": "sourceoci-serverless-copy",
  "oracle_endpoint_url": "https://<namespace>.compat.objectstorage.<oci region>.oraclecloud.com",
  "oracle_region": "<oci region>",
  "oracle_access_key_id": "******",
  "oracle_secret_access_key": "*********",
  "sns_topic_arn": "arn:aws:sns:******:********:*****",
  "dynamodb_table_name": "COPYOPERATIONS"
}
```

#### 9.  Encode the Event JSON to base64 and Test the Lambda function

```
$ base64 event.json > event_encoded.json
```

```
$ aws lambda invoke --function-name s3-to-oci --payload file://event_encoded.json response.json
```

If you get the below then the lambda invocation was successful
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST"
}
