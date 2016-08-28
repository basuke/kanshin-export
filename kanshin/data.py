# -*- coding: utf-8 -*-

import boto3
from boto3.dynamodb.conditions import Key

TABLE_PREFIX = 'KanshinCom-'
USER_TABLE = TABLE_PREFIX + 'user'
KEYWORD_TABLE = TABLE_PREFIX + 'keyword'
CONNECTION_TABLE = TABLE_PREFIX + 'connection'
DIARY_TABLE = TABLE_PREFIX + 'diary'

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
user_table = dynamodb.Table(USER_TABLE)
keyword_table = dynamodb.Table(KEYWORD_TABLE)
connection_table = dynamodb.Table(CONNECTION_TABLE)
diary_table = dynamodb.Table(DIARY_TABLE)

s3 = boto3.resource('s3', region_name='ap-northeast-1')
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

def save_user(item):
    item['id'] = int(item['id'])
    save_item(user_table, item)

def save_keyword(item):
    item['id'] = int(item['id'])
    save_item(keyword_table, item)

def save_connection(id1, id2, out_reason=None, in_reason=None):
    save_item(connection_table, dict(id=int(id1), other_id=int(id2), out_reason=out_reason, in_reason=in_reason), ['id', 'other_id'])

def save_diary(item):
    item['id'] = int(item['id'])
    save_item(diary_table, item)

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

def key_for(item, pk_keys):
    return dict([(key, item[key]) for key in item if key in pk_keys])

def updates_for(item, pk_keys):
    return dict([(key, {'Action': 'PUT', 'Value': item[key]}) for key in item if key not in pk_keys and item[key] is not None])

def save_item(table, item, pk_keys=['id']):
    table.update_item(
        Key=key_for(item, pk_keys),
        AttributeUpdates=updates_for(item, pk_keys)
    )

