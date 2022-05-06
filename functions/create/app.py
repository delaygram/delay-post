import os
import uuid
import time
from requests_toolbelt.multipart import decoder

import boto3
import botocore.exceptions
import json
from datetime import datetime
from aws_xray_sdk.core import patch_all

xray_patched = False

dynamo_db = boto3.resource('dynamodb', 'eu-west-3')
event_bus = boto3.client('events')
posts_table = dynamo_db.Table(os.environ.get('POSTS_TABLE'))
bucket_name = os.environ.get('BUCKET_NAME')
s3_client = boto3.client('s3')


def lambda_handler(event, context):
    global xray_patched
    if not xray_patched and 'DISABLE_XRAY' not in os.environ:
        patch_all()
        xray_patched = True

    print(event)

    body = json.loads(event['body'])
    print(body['file'])
    user_id = event['requestContext']['authorizer']['claims']['sub']
    filename_extension = body['file'].split('.')[-1]

    generated_filename = f'{user_id}-{time.time()}.{filename_extension}'

    presigned_url_response = {
        s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': generated_filename,
            },
            ExpiresIn=3600
        )
    }

    post = {
        'PK': user_id,
        'SK': generated_filename,
        'created_at': datetime.now(),
        'caption': body['caption'],

    }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'user_id': user_id,
            'upload_url': list(presigned_url_response).pop(),
            'generated_filename': generated_filename,
            'caption': body['caption']
        }),
    }
