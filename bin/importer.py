#!/usr/bin/env python3

import os.path
import sys
sys.path.insert(0, os.path.abspath('.'))

import logging
from kanshin.com.browser import KanshinBrowser
from kanshin.data import save_user, save_diary

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

def main(logger, *user_ids):
    logger.debug('start Kanshin browser')
    browser = KanshinBrowser()

    for user_id in user_ids:
        try:
            import_user(logger, browser, user_id)
        except:
            logger.err('failed to import user {}'.format(user_id))


def cli(argv):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    main(logger, *argv[1:])

if __name__ == '__main__':
    cli(sys.argv)
