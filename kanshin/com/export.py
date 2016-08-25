from kanshin.data import dynamodb, TABLE_PREFIX, has_image, save_image, save_item
from robobrowser.compat import urlparse
import requests
import boto3
from boto3.dynamodb.conditions import Key
import time


IMPORT_TABLE = TABLE_PREFIX + 'import'
import_table = dynamodb.Table(IMPORT_TABLE)

def import_image(url):
    path = urlparse.urlparse(url).path[1:]

    if not has_image(path):
        response = requests.get(url)
        if response.status_code != 200:
            return url

        content = response.content
        content_type = response.headers['Content-Type']
        save_image(path, content_type, content)

    return 'http://s.kanshin.link' + path

def key_for(kind, id):
	return '{kind}.{id}'.format(kind=kind, id=id)

def is_imported(kind, id):
	result = import_table.query(KeyConditionExpression=Key('id').eq(key_for(kind, id)))
	if 'Items' in result  and result['Items']:
		return result['Items'][0]
	else:
		return False

def mark_imported(kind, id):
	save_item(import_table, {'id': key_for(kind, id), 'timestamp': int(time.time() * 1000)})
