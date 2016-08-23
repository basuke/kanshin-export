#!/usr/bin/env python

import os.path
import sys
sys.path.insert(0, os.path.abspath('.'))

from kanshin.com.browser import KanshinBrowser
import re


def main():
    browser = KanshinBrowser()

    for link in browser.paginate_select('/sponsor/', '#indexUser h2 a'):
        tag, name = link.get('href').split('/').pop(), link.get_text()

        browser.open('/user/' + tag)

        rss = browser.select('.topicpath ul a')[0].get('href')
        pid = re.search(r'id=(\d+)', rss).group(1)

        print(pid, tag, name)


if __name__ == '__main__':
    main()
