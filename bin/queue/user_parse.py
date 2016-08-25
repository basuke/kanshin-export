#!/usr/bin/env python

from queue import *

from kanshin.com.user import UserPage
from kanshin.data import save_user
from kanshin.com.export import mark_imported

user_parse = queues.user_parse
image_download = queues.image_download

def job(user_id):
	page = fetch_page('user', user_id, UserPage)
	if page:
		record = page.record

		if record['image'] and is_kanshin_image_url(record['image']):
			record['image'] = convert_kanshin_image_url(record['image'])
			image_download.send(path_of_image(record['image']))

		logger.info('save user {}'.format(user_id))
		save_user(record)

		mark_imported('user', user_id)


cli(user_parse, job)
