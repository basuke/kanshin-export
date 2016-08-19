#!/usr/bin/env python3

import os.path
import sys
sys.path.insert(0, os.path.abspath('.'))

import click
from click import echo

import logging
from kanshin.com.browser import KanshinBrowser
from kanshin.data import save_user, save_diary

@click.command()
@click.option('--cache/--no-cache', default=False, help='use cache')
@click.argument('user', nargs=-1)
def importer(user, cache):
    """import user's diary from www.kanshin.com"""
    logger = create_logger()
    browser = KanshinBrowser(cache=cache)

    for user_id in user:
        try:
            import_user(logger, browser, user_id)
        except Exception as e:
            logger.exception('failed to import user {}'.format(user_id))

def import_user(logger, browser, user_id):
    user = None

    logger.debug('fetching diary ids for user id={id}'.format(id=user_id))
    diaries = browser.get_user_diaries(user_id)
    logger.debug('find {count} diaries'.format(count=len(diaries)))

    for info in diaries[:]:
        logger.debug('fetching diary:{title} id={id}'.format(**info))
        diary = browser.get_diary(info['id'])

        if not user:
            user = {'id': diary['user_id'], 'name': diary['user']}

        save_diary(diary)

    if user:
        user['imported'] = True
        save_user(**user)

def create_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    return logger

if __name__ == '__main__':
    importer()
