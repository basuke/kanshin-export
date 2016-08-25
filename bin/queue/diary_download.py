#!/usr/bin/env python

from queue import *

diary_download = queues.diary_download
diary_parse = queues.diary_parse

def job(diary_id):
	if download('diary', diary_id):
		diary_parse.send(diary_id)

cli(diary_download, job)
