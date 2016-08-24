#!/usr/bin/env python

from queue import *

from kanshin.com.browser import KanshinBrowser, URLError

def job(user_id):
    browser = KanshinBrowser()

    logger.info('collecting diary ids for user {}'.format(user_id))

    links = browser.paginate_select('/user/{uid}/diary'.format(uid=user_id), '.keyword h2 a')
    ids = [int(link.get('href').split('/').pop()) for link in links]

    logger.info('found {} diaries'.format(len(ids)))
    for diary_id in ids:
        diary_download.send(diary_id)

user_collect_diaries.listen(job)
