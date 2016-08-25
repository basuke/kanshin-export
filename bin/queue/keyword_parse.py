#!/usr/bin/env python

from queue import *

from kanshin.com.keyword import KeywordPage
from kanshin.data import save_keyword, save_connection
from kanshin.com.export import is_imported
from kanshin.com.browser import KanshinBrowser

keyword_parse = queues.keyword_parse
image_download = queues.image_download
user_download = queues.user_download
keyword_download = queues.keyword_download

def job(keyword_id):
    def with_html(html):
        page = KeywordPage(keyword_id, html)
        record = page.record

        if record['images']:
            record['images'] = convert_kanshin_images(record['images'], image_download)

        if page.more_comments:
            logger.info('download whole keyword comments for {}'.format(keyword_id))

            browser = KanshinBrowser()
            browser.open('/keyword/{kid}/comment'.format(kid=keyword_id))
            browser.save_page()
            record['comments'] = KeywordPage(keyword_id, browser.response.text).comments

        if page.more_connections:
            logger.info('download whole keyword connections for {}'.format(keyword_id))

            browser = KanshinBrowser()
            p = 1
            result = []
            while True:
                browser.open('/keyword/{kid}/connect?p={p}'.format(kid=keyword_id, p=p))
                browser.save_page()
                connections = KeywordPage(keyword_id, browser.response.text).connections
                if not connections:
                    break

                result += connections
                p += 1

            record['connections'] = result

        logger.info('save keyword {}'.format(keyword_id))
        connections = record['connections']
        del(record['connections'])
        save_keyword(record)

        ids = set()

        logger.info('save connections {}'.format(keyword_id))
        for connection in connections:
             # {'id': 11526,
             #  'out': u'iBook\u306b\u3064\u306a\u3052\u305f\u3044',
             #  'title': u'iBook\u306eUS\u30ad\u30fc\u30dc\u30fc\u30c9',
             #  'user': u'\u3046\u305a\u3089'}
            save_connection(record['id'], connection['id'], connection.get('out'), connection.get('in'))
            ids.add(connection['id'])

        for kid in ids:
            if not is_imported('keyword', kid):
                keyword_download.send(kid)

        ids = set([record['user_id']] + [comment['user_id'] for comment in record['comments']])
        for uid in ids:
            if not is_imported('user', uid):
                user_download.send(uid)

    page = fetch_page('keyword', keyword_id, with_html)


cli(keyword_parse, job)
