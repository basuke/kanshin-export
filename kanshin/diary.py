from . import Page, URL, extract_text
import re

class ListPage(Page):
    def __init__(self, user_id, p=1):
        super(ListPage, self).__init__('%s/user/%s/keyword?od=create&p=%s' % (URL, user_id, p))

    def keyword_pages(self):
        return sorted(list(set([link.get('href') for link in self.select('#content a[href^=/keyword/]')])), reverse=True)

class DetailPage(Page):
    def __init__(self, diary_id):
        self.diary_id = diary_id
        super(DetailPage, self).__init__('%s/diary/%s' % (URL, diary_id, ))

    @property
    def record(self):
        return {
            "id": self.diary_id,
            "title": self.title,
            "date": self.date,
            "text": self.text,
            "images": self.images,
            "user": self.user,
        }

    @property
    def title(self):
        return self.content('h2')

    @property
    def text(self):
        p = self.select('#entry .body p').pop()
        return extract_text(p)

    @property
    def images(self):
        url = [link.get('href') for link in self.select('.entryImages a')]
        return url

    @property
    def date(self):
        text = self.select('#entry .date').pop().get_text().replace('/', '-')
        return text

    @property
    def user(self):
        sec = self.select('.topicpath ul a')[0]
        name = sec.get_text().replace('の空間', '')
        uid = int(sec.get('href').split('/')[-1])
        return {'name': name, 'id': uid}
