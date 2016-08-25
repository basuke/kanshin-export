#!/usr/bin/env python

from queue import *

user_download = queues.user_download
user_parse = queues.user_parse
user_collect_keywords = queues.user_collect_keywords
user_collect_diaries = queues.user_collect_diaries

def job(user_id):
	if download('user', user_id):
		user_parse.send(user_id)
		user_collect_keywords.send(user_id)
		user_collect_diaries.send(user_id)

cli(user_download, job)
