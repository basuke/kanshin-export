# -*- coding: utf-8 -*-

import boto3
from boto3.dynamodb.conditions import Key
from urllib.parse import urlparse

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

def save_user(id, **fields):
    updates = dict([(key, {'Action': 'PUT', 'Value': fields[key]}) for key in fields])
    user_table.update_item(
        Key={'id': id},
        AttributeUpdates=updates
    )

def save_diary(diary):
    for comment in diary['comments']:
        save_user(comment['user_id'], name=comment['user'])

    images = [save_image(url) for url in diary['images']]

    diary_table.update_item(
        Key={'id': diary['id']},
        AttributeUpdates={
            'title': {'Action': 'PUT', 'Value': diary['title']},
            'text': {'Action': 'PUT', 'Value': diary['text']},
            'date': {'Action': 'PUT', 'Value': diary['date']},
            'user_id': {'Action': 'PUT', 'Value': diary['user_id']},
            'user': {'Action': 'PUT', 'Value': diary['user']},
            'images': {'Action': 'PUT', 'Value': images},
            'comments': {'Action': 'PUT', 'Value': diary['comments']},
        }
    )

def save_image(url):
    path = urlparse(url).path
    obj = storage_bucket.Object(path[1:])

    try:
        obj.metadata # test if obj exists
    except:
        response = requests.get(url)
        if response.status_code != 200:
            return url

        body = response.content
        content_type = response.headers['Content-Type']
        obj.put(Body=body, ContentType=content_type, ACL='public-read')

    return 'http://s.kanshin.link' + path

