#!/usr/bin/env python3
from time import sleep
import logging
from kanshin.com.browser import KanshinBrowser
import sys
import boto3
import decimal
from urllib.parse import urlparse
import requests

def dec(num):
    return decimal.Decimal(num)

TABLE_PREFIX = 'kanshin-com-'
USER_TABLE = TABLE_PREFIX + 'user'
DIARY_TABLE = TABLE_PREFIX + 'diary'

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
user_table = dynamodb.Table(USER_TABLE)
diary_table = dynamodb.Table(DIARY_TABLE)

s3 = boto3.resource('s3')
storage_bucket = s3.Bucket('s.kanshin.link')

def flatten_user(obj):
    if 'user' in obj and type(obj['user']) == dict:
        user = obj['user']
        obj['user_id'] = user['id']
        obj['user'] = user['name']
    return obj

def save_user(user):
    user_table.update_item(
        Key={'id': user['id']},
        AttributeUpdates={
            'name': {'Action': 'PUT', 'Value': user['name']},
        }
    )

def save_diary(diary):
    flatten_user(diary)

    for comment in diary['comments']:
        save_user(comment['user'])

    images = [save_image(url) for url in diary['images']]
    comments = [flatten_user(comment) for comment in diary['comments']]

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

def main(logger, email, password):
    logger.debug('start Kanshin browser')
    browser = KanshinBrowser()

    logger.debug('login with {user}'.format(user=email))
    browser.login(email, password)

    save_user(browser.user)

    diaries = browser.get_my_diaries()
    logger.debug('find {count} diaries'.format(count=len(diaries)))

    for info in diaries[:]:
        logger.debug('fetching diary:{title} id={id}'.format(**info))
        diary = browser.get_diary(info['id'])
        save_diary(diary)


def main2(logger, *user_ids):
    logger.debug('start Kanshin browser')
    browser = KanshinBrowser()

    for user_id in user_ids:
        user_saved = False

        logger.debug('fetching diary ids for user id={id}'.format(id=user_id))
        diaries = browser.get_user_diaries(user_id)
        logger.debug('find {count} diaries'.format(count=len(diaries)))

        for info in diaries[:]:
            logger.debug('fetching diary:{title} id={id}'.format(**info))
            diary = browser.get_diary(info['id'])

            if not user_saved:
                save_user(diary['user'])
                user_saved = True

            save_diary(diary)


def daemon(func, pid=None, log=None):
    if pid is None:
        pid = '/tmp/{name}.pid'.format(name=__name__)
    if log is None:
        log = '/tmp/{name}.log'.format(name=__name__)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    fh = logging.FileHandler(log, 'w+')
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    keep_fds = [fh.stream.fileno()]

    daemon = Daemonize(app=__name__, pid=pid, action=loop, keep_fds=keep_fds, logger=logger)
    daemon.start()

def cli(argv):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    main2(logger, *argv[1:])


# daemon(main)
cli(sys.argv)
