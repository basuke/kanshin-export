#!/usr/bin/env python

import os.path
import sys
sys.path.insert(0, os.path.abspath('.'))

import logging

logging.basicConfig(level=logging.WARNING)

from kanshin.utils.worker import Queue, logger
logger.setLevel(logging.INFO)

# queues

user_download = Queue('kanshin-com-user-download')
user_parse = Queue('kanshin-com-user-parse')
user_collect_keywords = Queue('kanshin-com-user-collect-keywords')
user_collect_diaries = Queue('kanshin-com-user-collect-diaries')
image_download = Queue('kanshin-com-image-download')
keyword_download = Queue('kanshin-com-keyword-download')
keyword_parse = Queue('kanshin-com-keyword-parse')
diary_download = Queue('kanshin-com-diary-download')
diary_parse = Queue('kanshin-com-diary-parse')

from kanshin.data import has_image, save_image
from robobrowser.compat import urlparse

def is_kanshin_image_url(url):
    return urlparse.urlparse(url).hostname == 'storage.kanshin.com'

def convert_kanshin_image_url(url):
    return 'http://s.kanshin.link' + path_of_image(url)

def path_of_image(url):
    return urlparse.urlparse(url).path
