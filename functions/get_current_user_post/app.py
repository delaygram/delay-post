import os
from datetime import datetime, timedelta

import boto3
import botocore.exceptions
import json

from aws_xray_sdk.core import patch_all
from boto3.dynamodb.conditions import Key

xray_patched = False

dynamo_db = boto3.resource('dynamodb', 'eu-west-3')
posts_table = dynamo_db.Table(os.environ.get('POSTS_TABLE'))


def lambda_handler(event, context):
    global xray_patched
    if not xray_patched and 'DISABLE_XRAY' not in os.environ:
        patch_all()
        xray_patched = True

    print(f'Received event: {event}')

    user_id = event['requestContext']['authorizer']['claims']['sub']

    response = posts_table.query(KeyConditionExpression=Key('PK').eq(user_id))

    print(type(response))
    print(response)

    if response['Count'] == 0:
        print(f'No posts found for user {user_id}')
        return {
            'statusCode': 204,
            'body': json.dumps({'message': f'No posts found for user {user_id}'})
        }
    else:
        print(f'Found {response["Count"]} posts for user {user_id}')
        return {
            'statusCode': 200,
            'body': json.dumps(list(map(dynamo_item_to_post_model, response['Items'])))
        }


def dynamo_item_to_post_model(post_item):
    return {
        'user_id': post_item['PK'],
        'image_name': post_item['SK'],
        'created_at': post_item['created_at'],
        'caption': post_item['caption'],
        'validated': post_item['validated']
    }
