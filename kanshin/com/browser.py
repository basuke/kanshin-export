from robobrowser import RoboBrowser
from robobrowser.compat import urlparse
import boto3
from .diary import DiaryPage

class KanshinError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class AuthError(KanshinError):
    def __init__(self, value="login is required"):
        super().__init__(value)

class URLError(KanshinError):
    def __init__(self, value="page not found"):
        super().__init__(value)

def login_only(func):
    def wrapper(self, *args, **kwargs):
        if not self.user:
            raise AuthError()
        return func(self, *args, **kwargs)

    return wrapper

s3 = boto3.resource('s3')
rip_bucket = s3.Bucket('raw.kanshin.rip')

class KanshinBrowser(RoboBrowser):
    def __init__(self, base_url='http://www.kanshin.com'):
        super().__init__(parser="html.parser")

        self.base_url = base_url
        self.user = None

    def open(self, url, method='get', **kwargs):
        if url[0:4] != 'http':
            url = urlparse.urljoin(self.base_url, url)

        super().open(url, method, **kwargs)

        if self.response.status_code == 404:
            raise URLError()

    def save_page(self):
        if not self.user:
            path = self.response.url.split('/', 3).pop()
            content_type = self.response.headers['content-type']
            content = self.response.text

            obj = rip_bucket.Object(path)
            obj.put(Body=content, ContentType=content_type, ACL='public-read')

    def login(self, email, password):
        self.logout()
        self.open('/login')

        form = self.get_form(action='/login')
        form['user'].value = email
        form['password'].value = password
        self.submit_form(form)

        if self.url.find('/home') < 0:
            raise "login unsuccessful"

        s = self.parsed

        uid = int(s.select('#remote a[href^=/user/]')[0].get('href').split('/').pop())
        name = s.select('h1').pop().get_text().replace('のマイページ', '')
        self.user = {'id':uid, 'name':name}

    def logout(self):
        if self.user:
            self.open('/logout')

            self.user = None

    @login_only
    def get_my_diaries(self):
        links = self.paginate_select('/home/diary', 'td.name a')
        return [{
            'id': int(link.get('href').split('/').pop()),
            'title': link.get('title')
        } for link in links]

    def get_user_diaries(self, user_id):
        links = self.paginate_select('/user/{uid}/diary'.format(uid=user_id), 'h3 a')
        return [{
            'id': int(link.get('href').split('/').pop()),
            'title': link.get_text()
        } for link in links]

    def get_diary(self, diary_id):
        self.open('/diary/{did}'.format(did=diary_id))
        self.save_page()

        record = DiaryPage(diary_id, self.parsed).record

        if self.parsed.select('.listNavAll a'):
            self.open('/diary/{did}/comment'.format(did=diary_id))
            self.save_page()
            record['comments'] = DiaryPage(diary_id, self.parsed).comments

        return record

    def get_bookmarked_users(self):
        if not self.user:
            return []

        links = self.paginate_select('/home/bookmark?show=user', 'td.name a')

        return [{
            'id': int(link.get('href').split('/').pop()),
            'name': link.get_text()
        } for link in links]

    def get_bookmarked_keywords(self):
        if not self.user:
            return []

        links = self.paginate_select('/home/bookmark?show=keyword', 'td.name a')

        return [{
            'id': int(link.get('href').split('/').pop()),
            'title': link.get_text()
        } for link in links]

    def paginate_select(self, url, selector):
        result = []
        page = 1
        count = 100

        while True:
            url += '?' if url.find('?') < 0 else '&'
            url += 'p={p}&cn={cn}'.format(p=page, cn=count)

            self.open(url)
            self.save_page()
            items = self.parsed.select(selector)
            if len(items) == 0:
                break

            result += items
            page += 1

        return result

