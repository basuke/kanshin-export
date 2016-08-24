#!/usr/bin/env python

from queue import *

from kanshin.com.cache import get_page, is_page_saved
from kanshin.com.user import UserPage
from kanshin.data import save_user

def job(user_id):

	path = '/user/{}'.format(user_id)

	if not is_page_saved(path):
		logger.warning('{} is not saved'.format(path))
		return

	_, html = get_page(path)

	record = UserPage(user_id, html).record

	if record['image'] and is_kanshin_image_url(record['image']):
		record['image'] = convert_kanshin_image_url(record['image'])
		image_download.send(path_of_image(record['image']))

	logger.info('save user {}'.format(user_id))
	save_user(record)

user_parse.listen(job)
