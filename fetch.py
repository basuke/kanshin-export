import sys
from bs4 import BeautifulSoup
import requests
import re
import json

URL = 'http://www.kanshin.com'

def full_url(url):
    if url.startswith('/'):
        url = URL + url
    return url

class Page(object):
    def __init__(self, url):
        self.url = full_url(url)

        self.response = requests.get(self.url)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

    @property
    def html(self):
        return self.response.text

    @property
    def status_code(self):
        return self.response.status_code

    def find(self, tag):
        return self.soup.find_all(tag)

    def select(self, selector):
        return self.soup.select(selector)

    def select1(self, selector):
        result = self.select(selector)
        if len(result) == 0:
            return None

        return result[0]

    def content(self, selector):
        result = self.select1(selector)
        if result is None:
            return None

        return result.get_text().strip()

    def find_links(self, pattern=None):
        urls = map(lambda link: link.get('href'), self.find('a'))
        return [url for url in urls if url and (pattern is None or pattern.search(url))]

class KeywordListPage(Page):
    def __init__(self, user_id, p=1):
        super(KeywordListPage, self).__init__('http://www.kanshin.com/user/%s/keyword?od=create&p=%s' % (user_id, p))

    def keyword_pages(self):
        return sorted(list(set([link.get('href') for link in self.select('#content a[href^=/keyword/]')])), reverse=True)

class KeywordPage(Page):
    def __init__(self, keyword_id):
        super(KeywordPage, self).__init__('http://www.kanshin.com/keyword/%s' % (keyword_id, ))

    @property
    def title(self):
        return self.content('h1.title')

    @property
    def title_yomi(self):
        return self.content('p.titleYomi')

    @property
    def text(self):
        text = self.select('.colMain p').pop().get_text()
        return text

def fetch_keywords(user_id, offset=0, limit=1000):
    list_page = KeywordListPage(user_id)
    keywords = []
    for url in list_page.keyword_pages()[offset:limit]:
        print url
        match = re.search('''^/keyword/(\d+)''', url)
        if match:
            keyword_id = int(match.group(1))
            keyword = KeywordPage(keyword_id)
            print keyword_id, keyword.title
            keywords.append({"id": keyword_id, "title": keyword.title, "title_yomi": keyword.title_yomi, "text": keyword.text})

    return keywords

def main(user_id=0):
    if user_id <= 0:
        usage()
        sys.exit()

    keywords = fetch_keywords(user_id)
    print json.dumps(keywords, indent=2)

if __name__ == '__main__':
    main(*sys.argv[1:])
