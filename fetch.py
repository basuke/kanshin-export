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

class Loader(object):
    def __init__(self, use_cache=False):
        self.use_cache = use_cache

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
        self.keyword_id = keyword_id
        super(KeywordPage, self).__init__('http://www.kanshin.com/keyword/%s' % (keyword_id, ))

    @property
    def record(self):
        return {
            "id": self.keyword_id,
            "title": self.title,
            "title_yomi": self.title_yomi,
            "text": self.text,
            "images": self.images,
            "created": self.created,
            "updated": self.updated,
            "viewed": self.viewed,
            "category": self.category,
            "user": self.user,
            "attributes": self.attributes,
        }

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

    @property
    def images(self):
        url = [link.get('href') for link in self.select('.entryImages a')]
        return url

    def get_stats(self):
        ul = self.select('.keywordAttributeSection ul').pop() # last UL in attributes section
        items = ul.select('li')
        viewed = int(items.pop().get_text().strip().replace('クリック', ''))
        created = items.pop().get_text().strip().replace('登録', '').replace('/', '-')
        if items:
            updated = items.pop().get_text().strip().replace('更新', '').replace('/', '-')
        else:
            updated = created

        return [created, updated, viewed]


    @property
    def created(self):
        return self.get_stats()[0]

    @property
    def updated(self):
        return self.get_stats()[1]

    @property
    def viewed(self):
        return self.get_stats()[2]

    @property
    def category(self):
        ul = self.select('.keywordAttributeSection ul')[0] # first UL in attributes section
        link = ul.select('a')[0]
        name = link.get_text()
        cid = int(link.get('href').split('=')[1])
        return {'name': name, 'id': cid}

    @property
    def user(self):
        sec = self.select('.userProfileSection')[0]
        name = sec.select('.head')[0].get_text()
        uid = int(sec.select('a')[0].get('href').split('/')[-1])
        return {'name': name, 'id': uid}

    @property
    def attributes(self):
        attributes = []

        items = self.select('#keywordAttribute li')
        items += self.select('#mappedKeywordAttribute li') # Amazon商品情報の場合

        for li in items:
            key = li.select('.key')
            value = li.select('.value')
            if key and value:
                item = {
                    'name': key[0].get_text().split(':')[0],
                    'value': value[0].get_text().strip()
                }
                attributes.append(item)
            else:
                link = li.select('a')
                if link:
                    attributes.append({'name': 'URL', 'value': link[0].get('href')})


        return attributes


def fetch_keywords(user_id, offset=0, limit=10000):
    list_page = KeywordListPage(user_id)
    keywords = []
    for url in list_page.keyword_pages()[offset:limit]:
        print(url)
        match = re.search('''^/keyword/(\d+)''', url)
        if match:
            keyword_id = int(match.group(1))
            keyword = KeywordPage(keyword_id)
            print(keyword_id, keyword.title)
            keywords.append(keyword.record)

    return keywords

def main(user_id=0):
    user_id = int(user_id)
    if user_id <= 0:
        usage()
        sys.exit()

    keywords = fetch_keywords(user_id)
    print(json.dumps(keywords, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main(*sys.argv[1:])
