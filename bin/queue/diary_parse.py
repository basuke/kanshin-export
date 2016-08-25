#!/usr/bin/env python

from queue import *

from kanshin.com.diary import DiaryPage
from kanshin.data import save_diary
from kanshin.com.export import is_imported
from kanshin.com.browser import KanshinBrowser

diary_parse = queues.diary_parse
image_download = queues.image_download
user_download = queues.user_download

def job(diary_id):
    def with_html(html):
        page = DiaryPage(diary_id, html)
        record = page.record

        if record['images']:
            record['images'] = convert_kanshin_images(record['images'], image_download)

        if page.more_comments:
            logger.info('download whole diary comments for {}'.format(diary_id))

            browser = KanshinBrowser()
            browser.open('/diary/{kid}/comment'.format(kid=diary_id))
            browser.save_page()
            record['comments'] = DiaryPage(diary_id, browser.response.text).comments

        logger.info('save diary {}'.format(diary_id))
        save_diary(record)

        ids = set([record['user_id']] + [comment['user_id'] for comment in record['comments']])
        for user_id in ids:
            if not is_imported('user', user_id):
                user_download.send(user_id)

    page = fetch_page('diary', diary_id, with_html)

cli(diary_parse, job)
