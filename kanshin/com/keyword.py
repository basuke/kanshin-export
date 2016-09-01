# -*- coding: utf-8 -*-

from . import Page, URL, extract_text, build_user
from bs4.element import Tag
import re

class KeywordPage(Page):
    def __init__(self, keyword_id, data):
        self.keyword_id = keyword_id
        super(KeywordPage, self).__init__('%s/keyword/%s' % (URL, keyword_id, ), data)

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
            "user_id": self.user['id'],
            "user": self.user['name'],
            "attributes": self.attributes,
            "comments": self.comments,
            "connections": self.connections,
        }

    @property
    def title(self):
        return self.content('h1.title')

    @property
    def title_yomi(self):
        return self.content('p.titleYomi')

    @property
    def text(self):
        node = self.select('.colMain p').pop()
        return extract_text(node)

    @property
    def images(self):
        url = [link.get('href') for link in self.select('.entryImages a')]
        return url

    def get_stats(self):
        ul = self.select('.keywordAttributeSection ul').pop() # last UL in attributes section
        items = ul.select('li')
        viewed = int(items.pop().get_text().strip().replace(u'クリック', ''))
        created = items.pop().get_text().strip().replace(u'登録', '').replace('/', '-')
        if items:
            updated = items.pop().get_text().strip().replace(u'更新', '').replace('/', '-')
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
        try:
            ul = self.select('.keywordAttributeSection ul')[0] # first UL in attributes section
            link = ul.select('a')[0]
            name = link.get_text()
            cid = int(link.get('href').split('=')[1])
        except:
            name, cid = u'ノンカテゴリー', 1000

        return {'name': name, 'id': cid}

    @property
    def user(self):
        sec = self.select('.userProfileSection')[0]
        name = sec.select('.head')[0].get_text()
        uid = sec.select('a')[0].get('href').split('/')[-1]
        return build_user(uid, name)

    @property
    def attributes(self):
        attributes = []

        items = self.select('#keywordAttribute li')
        items += self.select('#mappedKeywordAttribute li') # Amazon商品情報の場合

        for li in items:
            key = li.select('.key')
            value = li.select('.value')
            if key and value:
                name = key[0].get_text().split(':')[0]
                value = value[0].get_text().strip()

                if name and value:
                    attributes.append({'name': name, 'value': value})
            else:
                link = li.select('a')
                if link:
                    attributes.append({'name': 'URL', 'value': link[0].get('href')})


        return attributes

    @property
    def more_comments(self):
        return len(self.select('#comment .listNavAll')) > 0

    @property
    def comments(self):
        try:
            container = self.select('#comment div.body')[0]
        except:
            return []

        items = (item for item in container.contents if type(item) == Tag)
        comments = []
        date = None
        for item in items:
            if not item.get_text():
                continue
            if item.name == 'h3': # date
                date = item.get_text().replace('/', '-')
            elif not item.get('class'):
                texts = [t for t in item.contents[2:] if type(t) != Tag or not t.get('onclick')]
                text = extract_text(texts).rstrip()

                link = item.select('a')[0]
                name = link.get_text()
                uid = link.get('href').split('/')[-1]
                user = build_user(uid, name)

                comment = {
                    'user_id': user['id'],
                    'user': user['name'],
                    'text': text,
                    'date': date,
                }

                if 'tag' in user:
                    comment['tag'] = user['tag']

                if text and date:
                    comments.append(comment)

        return comments


    @property
    def more_connections(self):
        return len(self.select('#connection .listNavAll')) > 0


    @property
    def connections(self):
        def reason(links):
            str = links[0].get_text().replace(u'つながり', '')
            return str if str else 'つながり'

        connections = []
        connection = {}
        for div in self.select('#connection > div'):
            cls = div.get('class')
            if 'connectionReason' in cls:
                for li in div.select('li'):
                    cls = li.get('class')
                    if 'connectionReasonOut' in cls:
                        links = li.select('a[href^=/connect/]')
                        if links:
                            connection['in'] = reason(links)

                    if 'connectionReasonIn' in cls:
                        links = li.select('a[href^=/connect/]')
                        if links:
                            connection['out'] = reason(links)

            elif 'item' in cls:
                link = div.select('h3 a')[0]
                connection['id'] = int(link.get('href').split('/')[-1])
                connection['title'] = link.get_text().strip()
                connection['user'] = div.select('ul li')[0].get_text()[1:-1]
                connections.append(connection)

                connection = {}

        return connections

