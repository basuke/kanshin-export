#!/usr/bin/env python

from queue import *

from kanshin.com.browser import KanshinBrowser, URLError

user_collect_diaries = queues.user_collect_diaries
diary_download = queues.diary_download

def job(user_id):
    browser = KanshinBrowser()

    logger.info('collecting diary ids for user {}'.format(user_id))

    for diary in browser.get_user_diaries(user_id):
        diary_download.send(diary['id'])

cli(user_collect_diaries, job)
