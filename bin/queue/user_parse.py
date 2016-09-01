#!/usr/bin/env python

from queue import *

from kanshin.com.user import UserPage
from kanshin.data import save_user
import kanshin.com.sponsor


user_parse = queues.user_parse
image_download = queues.image_download

def job(user_id):
    def with_html(html):
        page = UserPage(user_id, html)
        record = page.record

        if record['image'] and is_kanshin_image_url(record['image']):
            record['image'] = convert_kanshin_image_url(record['image'])
            image_download.send(path_of_image(record['image']))

        logger.info('save user {}'.format(user_id))
        save_user(record)

    tag = kanshin.com.sponsor.find_tag(int(user_id))

    fetch_page('user', user_id, with_html, '/user/' + (tag if tag else user_id))

cli(user_parse, job)
