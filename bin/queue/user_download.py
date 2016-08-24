#!/usr/bin/env python

from queue import *

from kanshin.com.browser import KanshinBrowser, URLError
from kanshin.com.cache import is_page_saved

def job(user_id):
	path = '/user/{}'.format(user_id)

	if is_page_saved(path):
		logger.info('{} is already saved'.format(path))
		return

	browser = KanshinBrowser()

	logger.info('downloading ' + path)
	try:
		browser.open(path)

		logger.info('saving ' + path)
		browser.save_page()

		user_parse.send(user_id)
		user_collect_keywords.send(user_id)
		user_collect_diaries.send(user_id)
	except URLError as e:
		logger.error(e)
		pass

user_download.listen(job)
