# -*- coding: utf-8 -*-

from . import Page, URL, extract_text, extract_user
from bs4.element import Tag
import re

class UserPage(Page):
    def __init__(self, user_id, soup=None):
        self.user_id = user_id
        super(UserPage, self).__init__('%s/user/%s' % (URL, user_id, ), soup)

    @property
    def record(self):
        return {
            "id": self.id,
            "tag": self.tag,
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "profile": self.profile,
            "website": self.website,
            "image": self.image,
            "twitter": self.twitter,
        }

    @property
    def id(self):
        rss = self.select('.topicpath ul a')[0].get('href')
        pid = re.search(r'id=(\d+)', rss).group(1)
        return int(pid)

    @property
    def tag(self):
        return self.user_id if not re.match('''\d+''', '{}'.format(self.user_id)) else None

    @property
    def name(self):
        name = self.select('.topicpath h1')[0].get_text().replace(u'の空間', '')
        return name.strip()

    def _stat(self):
        sub = self.select('.userAttributeSection li')
        img = sub.pop(0).select('a')[0].get('href') if len(sub) > 2 else None
        updated = sub.pop(0).get_text().strip().replace(u'更新', '').replace('/', '-')
        created = sub.pop(0).get_text().strip().replace(u'登録', '').replace('/', '-')
        return (img, updated, created)

    @property
    def created(self):
        return self._stat()[2]

    @property
    def updated(self):
        return self._stat()[1]

    @property
    def profile(self):
        texts = self.select('#profile .userProfileSection p')[0]
        return extract_text(texts.contents)

    @property
    def website(self):
        links = self.select('#profile .userProfileSection li a')
        print(links)
        if links:
            return links[0].get('href')
        return None

    @property
    def image(self):
        return self._stat()[0]

    @property
    def twitter(self):
        links = self.select('#profile .userProfileSection .twitterAccount a')
        if links:
            return links[0].get('href').split('/').pop()
        return None

