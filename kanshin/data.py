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

