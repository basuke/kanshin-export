#!/usr/bin/env python

from queue import *

from kanshin.com.keyword import KeywordPage
from kanshin.data import save_keyword
from kanshin.com.export import mark_imported

keyword_parse = queues.keyword_parse
image_download = queues.image_download

def job(keyword_id):
	page = fetch_page('keyword', keyword_id, KeywordPage)
	if page:
		record = page.record

		if record['images']:
			record['images'] = convert_kanshin_images(record['images'], image_download)

		logger.info('save keyword {}'.format(keyword_id))
		save_keyword(record)

		mark_imported('keyword', keyword_id)


cli(keyword_parse, job)
