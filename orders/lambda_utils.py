import boto3
import json

# Create a Lambda client
lambda_client = boto3.client('lambda', region_name='us-east-1')  # Change to your region

def invoke_lambda(event_data):
    try:
        # Invoke the Lambda function
        response = lambda_client.invoke(
            FunctionName='SendEmailFromSES',  # Lambda function name
            InvocationType='RequestResponse',  # 'Event' for async
            Payload=json.dumps(event_data)  # Event data to pass to Lambda
        )

        # Read and return the response from Lambda
        result = response['Payload'].read().decode('utf-8')
        return result
    except Exception as e:
        return str(e)