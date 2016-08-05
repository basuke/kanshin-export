#!/usr/bin/env python3
from time import sleep
import logging
from kanshin.browser import KanshinBrowser
import sys
import boto3
import decimal

def dec(num):
    return decimal.Decimal(num)

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
diary_table = dynamodb.Table('kanshin-com-diary')
diary_comment_table = dynamodb.Table('kanshin-com-diary-comment')
user_table = dynamodb.Table('kanshin-com-user')

def save_user(user):
    response = user_table.put_item(
       Item={
            'id': dec(user['id']),
            'name': user['name'],
        }
    )

def save_diary(diary):
    uids = []

    response = diary_table.put_item(
        Item={
            'id': diary['id'],
            'title': diary['title'],
            'text': diary['text'],
            'date': diary['date'],
            'images': diary['images'],
            'user': diary['user'],
            'comments': diary['comments'],
        }
    )

    for comment in diary['comments']:
        save_user(comment['user'])

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

    main(logger, *argv[1:3])


# daemon(main)
cli(sys.argv)
