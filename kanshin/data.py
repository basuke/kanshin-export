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
    query_args = dict(
        IndexName='byUser',
        KeyConditionExpression=Key('user_id').eq(user_id),
        ProjectionExpression='id'
    )

    for item in query(diary_table, **query_args):
        yield(get_item(diary_table, item['id']))


def fetch_user_keywords(user_id):
    query_args = dict(
        IndexName='byUser',
        KeyConditionExpression=Key('user_id').eq(user_id),
        ProjectionExpression='id'
    )

    for item in query(keyword_table, **query_args):
        yield(get_item(keyword_table, item['id']))


def fetch_user(user_id):
    return get_item(user_table, user_id)


def fetch_connections(keyword_id):
    query_args = dict(
        IndexName='byUser',
        KeyConditionExpression=Key('user_id').eq(user_id),
        ProjectionExpression='id'
    )

    return (
        dict(
            id=item['other_id'],
            out_reason=item['out_reason'],
            in_reason=item['in_reason']
        )
        for item in query(connection_table, **query_args)
    )


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

def get_item(table, id=None, **kwargs):
    if id is not None:
        kwargs['KeyConditionExpression'] = Key('id').eq(id)

    result = table.query(**kwargs)
    if result['Items'] and len(result['Items']) > 0:
        return result['Items'][0]
    else:
        return None


def query(table, **kwargs):
    startKey = None

    while True:
        if startKey:
            kwargs['ExclusiveStartKey'] = startKey
        elif 'ExclusiveStartKey' in kwargs:
            del kwargs['ExclusiveStartKey']

        result = table.query(**kwargs)
        for item in result['Items']:
            yield item

        startKey = result.get('LastEvaluatedKey')
        if not startKey:
            break


def key_for(item, pk_keys):
    return dict([(key, item[key]) for key in item if key in pk_keys])


def updates_for(item, pk_keys):
    updates = {}

    for key in item:
        if key not in pk_keys:
            value = item[key]

            if value is None or value == '':
                value = {'Action': 'DELETE'}
            else:
                value = {'Action': 'PUT', 'Value': value}

            updates[key] = value

    return updates


def save_item(table, item, pk_keys=['id']):
    table.update_item(
        Key=key_for(item, pk_keys),
        AttributeUpdates=updates_for(item, pk_keys)
    )

