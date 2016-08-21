# -*- coding: utf-8 -*-

import boto3
from boto3.dynamodb.conditions import Key

TABLE_PREFIX = 'kanshin-com-'
USER_TABLE = TABLE_PREFIX + 'user'
DIARY_TABLE = TABLE_PREFIX + 'diary'

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
user_table = dynamodb.Table(USER_TABLE)
diary_table = dynamodb.Table(DIARY_TABLE)

s3 = boto3.resource('s3')
storage_bucket = s3.Bucket('s.kanshin.link')

def fetch_user_diaries(user_id):
    result = diary_table.query(IndexName='user_id-date-index-copy', KeyConditionExpression=Key('user_id').eq(user_id))
    return result['Items']

def fetch_user(user_id):
	result = user_table.query(KeyConditionExpression=Key('id').eq(user_id))
	if 'Items' in result  and result['Items']:
		return result['Items'][0]
	else:
		return None

def save_user(user):
    save_item(user_table, user)

def save_diary(diary):
    for comment in diary['comments']:
        save_user(dict(id=comment['user_id'], name=comment['user']))

    save_item(diary_table, diary)

def has_image(path):
    obj = storage_bucket.Object(path)

    try:
        obj.metadata # test if obj exists
    except:
        return False

    return True

def save_image(path, content_type, content):
    obj = storage_bucket.Object(path)
    obj.put(Body=content, ContentType=content_type, ACL='public-read')

# ----------------------

def save_item(table, item):
    updates = dict([(key, {'Action': 'PUT', 'Value': item[key]}) for key in item if key != 'id'])
    table.update_item(
        Key={'id': item['id']},
        AttributeUpdates=updates
    )

