#!/usr/bin/env python

import os.path
import sys
sys.path.insert(0, os.path.abspath('.'))

import click
from click import echo

import logging
from kanshin.com.browser import KanshinBrowser
from kanshin.data import save_user, save_diary
from kanshin.com.export import import_image

@click.command()
@click.option('--cache/--no-cache', default=False, help='use cache')
@click.argument('user', nargs=-1)
def importer(user, cache):
    """import user's diary from www.kanshin.com"""
    browser = KanshinBrowser(cache=cache)

    for user_id in user:
        try:
            import_user(browser, user_id)
        except Exception as e:
            logger.exception(u'failed to import user {}'.format(user_id))

def import_user(browser, user_id):
    user = None

    logger.debug(u'fetching diary ids for user id={id}'.format(id=user_id))

    diaries = browser.get_user_diaries(user_id)
    logger.debug(u'find {count} diaries'.format(count=len(diaries)))

    for info in diaries[:]:
        logger.debug(u'fetching diary:{title} id={id}'.format(**info))
        diary = browser.get_diary(info['id'])

        if not user:
            user = {'id': diary['user_id'], 'name': diary['user']}

        diary['images'] = [import_image(url) for url in diary['images']]

        save_diary(diary)

    if user:
        user['imported'] = True
        save_user(user)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

if __name__ == '__main__':
    importer()
