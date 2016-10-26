#!/usr/bin/env python

from queue import *
from kanshin.com.browser import KanshinBrowser, URLError
from kanshin.com import extract_user


user_download = queues.user_download
browser = KanshinBrowser()

logger.info('collecting user ids')

links = browser.paginate_select('/user/?od=create&cn=100', '.user h2 a')
for link in links:
    user = extract_user(link)
    user_download.send(user['id'])
