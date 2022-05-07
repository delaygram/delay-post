import os

import boto3
import botocore.exceptions
import json

from aws_xray_sdk.core import patch_all

dynamo_db = boto3.resource('dynamodb', 'eu-west-3')
posts_table = dynamo_db.Table(os.environ.get('POSTS_TABLE'))



def lambda_handler(event, context):
    global xray_patched
    if not xray_patched and 'DISABLE_XRAY' not in os.environ:
        patch_all()
        xray_patched = True

    print(f'Received event: {event}')

    body = json.loads(event['body'])
    print(f'Body: {body}')
    user_id = event['requestContext']['authorizer']['claims']['sub']
    validated = True

    item = posts_table.get_item(
        Key={
            'PK': user_id,
            'SK': body['generated_filename']
        }
    )

    print(f'Item: {item}')


    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
            # "location": ip.text.replace("\n", "")
        }),
    }