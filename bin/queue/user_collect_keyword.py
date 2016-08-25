#!/usr/bin/env python

from queue import *

from kanshin.com.browser import KanshinBrowser, URLError

user_collect_keywords = queues.user_collect_keywords
keyword_download = queues.keyword_download

def job(user_id):
    browser = KanshinBrowser()

    logger.info('collecting keyword ids for user {}'.format(user_id))

    for keyword in browser.get_user_keywords(user_id):
        keyword_download.send(keyword['id'])

cli(user_collect_keywords, job)
