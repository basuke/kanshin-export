#!/usr/bin/env python

from queue import *

from kanshin.com.browser import KanshinBrowser, URLError

def job(user_id):
    browser = KanshinBrowser()

    logger.info('collecting keyword ids for user {}'.format(user_id))

    links = browser.paginate_select('/user/{uid}/keyword'.format(uid=user_id), 'h3 a')
    ids = [int(link.get('href').split('/').pop()) for link in links]

    logger.info('found {} keywords'.format(len(ids)))
    for keyword_id in ids:
        keyword_download.send(keyword_id)

user_collect_keywords.listen(job)
