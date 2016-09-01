#!/usr/bin/env python

import os.path
import sys

sys.path.insert(0, os.path.abspath('.'))

import logging
from kanshin.utils.worker import Queue
from kanshin.data import has_image, save_image
from robobrowser.compat import urlparse
from kanshin.com.export import is_imported, mark_imported
from kanshin.com.browser import KanshinBrowser, URLError
from kanshin.com.cache import get_page, is_page_saved

program = sys.argv[0]
argv = sys.argv[1:]

logging.basicConfig(level=logging.WARNING)

logger = logging.getLogger('main')
logger.setLevel(logging.INFO)


# queues

class QueueFactory(object):
    @property
    def user_download(self):
        return Queue('kanshin-com-user-download')

    @property
    def user_parse(self):
        return Queue('kanshin-com-user-parse')

    @property
    def user_collect_keywords(self):
        return Queue('kanshin-com-user-collect-keywords')

    @property
    def user_collect_diaries(self):
        return Queue('kanshin-com-user-collect-diaries')

    @property
    def image_download(self):
        return Queue('kanshin-com-image-download')

    @property
    def keyword_download(self):
        return Queue('kanshin-com-keyword-download')

    @property
    def keyword_parse(self):
        return Queue('kanshin-com-keyword-parse')

    @property
    def diary_download(self):
        return Queue('kanshin-com-diary-download')

    @property
    def diary_parse(self):
        return Queue('kanshin-com-diary-parse')

queues = QueueFactory()


def is_kanshin_image_url(url):
    return urlparse.urlparse(url).hostname == 'storage.kanshin.com'


def convert_kanshin_image_url(url):
    return 'http://s.kanshin.link' + path_of_image(url)


def path_of_image(url):
    return urlparse.urlparse(url).path


def convert_kanshin_images(urls, q):
    result = []

    for url in urls:
        if is_kanshin_image_url(url):
            url = convert_kanshin_image_url(url)
            q.send(path_of_image(url))

        result.append(url)

    return result


def download(kind, id):
    path = '/{kind}/{id}'.format(kind=kind, id=id)

    if is_imported(kind, id):
        logger.info('{} is already imported'.format(path))
        return False

    if is_page_saved(path):
        logger.info('{} is already saved'.format(path))
    else:
        browser = KanshinBrowser()

        logger.info('downloading ' + path)
        try:
            browser.open(path)

            logger.info('saving ' + path)
            browser.save_page()
        except URLError as e:
            logger.error(e)
            pass

    return True


def fetch_page(kind, id, action, path=None):
    path = path if path else '/{kind}/{id}'.format(kind=kind, id=id)

    if is_imported(kind, id):
        # logger.info('{} is already imported'.format(path))
        return None

    if not is_page_saved(path):
        logger.warning('{} is not saved'.format(path))
        return None

    _, html = get_page(path)

    action(html)

    mark_imported(kind, id)


def cli(queue, job):
    if argv:
        for arg in argv:
            job(arg)
    else:
        queue.listen(job)

