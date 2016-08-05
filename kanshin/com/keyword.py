from . import Page, URL, extract_text
import re

class ListPage(Page):
    def __init__(self, user_id, p=1):
        super(ListPage, self).__init__('%s/user/%s/keyword?od=create&p=%s' % (URL, user_id, p))

    def keyword_pages(self):
        return sorted(list(set([link.get('href') for link in self.select('#content a[href^=/keyword/]')])), reverse=True)

class DetailPage(Page):
    def __init__(self, keyword_id):
        self.keyword_id = keyword_id
        super(DetailPage, self).__init__('%s/keyword/%s' % (URL, keyword_id, ))

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
        node = self.select('.colMain p').pop()
        return extract_text(node)

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


