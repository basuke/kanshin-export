from bs4 import BeautifulSoup
import requests

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

