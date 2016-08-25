#!/usr/bin/env python

from queue import *

keyword_download = queues.keyword_download
keyword_parse = queues.keyword_parse

def job(keyword_id):
	if download('keyword', keyword_id):
		keyword_parse.send(keyword_id)

cli(keyword_download, job)
