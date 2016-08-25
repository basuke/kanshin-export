#!/usr/bin/env python

from queue import *

from kanshin.com.cache import is_page_saved
from kanshin.data import has_image, save_image
import requests

def job(path):
    if has_image(path[1:]):
        logger.info('image has already saved: ' + path)
    else:
        logger.info('downloading image: ' + path)
        response = requests.get('http://storage.kanshin.com' + path)
        if response.status_code == 200:
            logger.info('saving image: ' + path)

            content = response.content
            content_type = response.headers['Content-Type']
            save_image(path[1:], content_type, content)

            logger.info('saved image: ' + path)
        else:
            logger.warning('image cannot downloaded with status code {}: {}'.format(response.status_code, path))

cli(queues.image_download, job)
