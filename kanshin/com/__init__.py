from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
import requests
from . import sponsor


URL = 'http://www.kanshin.com'
LINK_FORMAT = '[{text}]({url})'

class Page(object):
    def __init__(self, url, soup=None):
        self.url = url

        if soup:
            self.soup = soup
        else:
            response = requests.get(self.url)
            self.soup = BeautifulSoup(response.text, 'html.parser')

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

def extract_text(contents):
    text = ''
    for node in contents:
        if isinstance(node, NavigableString):
            text += str(node)
        elif isinstance(node, Tag):
            if node.name == 'a':
                text += LINK_FORMAT.format(url=node.get('href'), text=node.get_text())
    return text

def extract_user(link):
    name = link.get_text()
    uid = link.get('href').split('/')[-1]

    info = sponsor.find(uid)
    if info:
        return info
    else:
        return {'id': int(uid), 'name': name}

