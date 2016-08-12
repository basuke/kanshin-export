from . import Page, URL, extract_text
from bs4.element import Tag

class DiaryPage(Page):
    def __init__(self, diary_id, soup=None):
        self.diary_id = diary_id
        super().__init__('%s/diary/%s' % (URL, diary_id, ), soup)

    @property
    def record(self):
        return {
            "id": self.diary_id,
            "title": self.title,
            "date": self.date,
            "text": self.text,
            "images": self.images,
            "user": self.user,
            "comments": self.comments,
        }

    @property
    def title(self):
        return self.content('h2')

    @property
    def text(self):
        p = self.select('#entry .body p').pop()
        return extract_text(p.contents)

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

    @property
    def comments(self):
        container = self.select('#comment div.body')[0]
        items = (item for item in container.contents if type(item) == Tag)
        comments = []
        date = None
        for item in items:
            if item.name == 'h3':
                date = item.get_text().replace('/', '-')
            elif not item.get('class'):
                texts = [t for t in item.contents[2:] if type(t) != Tag or not t.get('onclick')]
                text = extract_text(texts).rstrip()

                link = item.select('a')[0]
                name = link.get_text()
                uid = int(link.get('href').split('/')[-1])
                user =  {'name': name, 'id': uid}

                comments.append({
                    'user': user,
                    'text': text,
                    'date': date,
                })

        return comments
