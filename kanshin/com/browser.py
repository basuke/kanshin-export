# -*- coding: utf-8 -*-

from robobrowser import RoboBrowser
from robobrowser.compat import urlparse
import boto3
from .diary import DiaryPage
import requests_cache
import sys

class KanshinError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class AuthError(KanshinError):
    def __init__(self, value="login is required"):
        super(AuthError, self).__init__(value)

class URLError(KanshinError):
    def __init__(self, url, value="page not found: "):
        super(URLError, self).__init__(value + url)

s3 = boto3.resource('s3')
rip_bucket = s3.Bucket('raw.kanshin.rip')

CACHE_NAME = '.kanshin-cache-{}.{}'.format(*sys.version_info[0:2])


class KanshinBrowser(RoboBrowser):
    def __init__(self, base_url='http://www.kanshin.com', cache=False):
        if cache:
            print('caching in {}'.format(CACHE_NAME))
            requests_cache.install_cache(CACHE_NAME)

        super(KanshinBrowser, self).__init__(parser="html.parser", history=2)

        self.base_url = base_url
        self.user = None

    def open(self, url, method='get', **kwargs):
        if url[0:4] != 'http':
            url = urlparse.urljoin(self.base_url, url)

        super(KanshinBrowser, self).open(url, method, **kwargs)

        if self.response.status_code == 404:
            raise URLError(url)

    def save_page(self):
        if not self.user:
            path = urlparse.urlparse(self.response.url).path[1:]
            content_type = self.response.headers['content-type']
            content = self.response.text

            obj = rip_bucket.Object(path)
            obj.put(Body=content, ContentType=content_type, ACL='public-read')

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

    def paginate_select(self, url, selector):
        result = []
        page = 1
        count = 100
        url += '?' if url.find('?') < 0 else '&'

        while True:
            tmp_url = url + 'p={p}&cn={cn}'.format(p=page, cn=count)

            self.open(tmp_url)
            self.save_page()
            items = self.parsed.select(selector)
            if len(items) == 0:
                break

            result += items
            page += 1

        return result

def login_only(func):
    def wrapper(self, *args, **kwargs):
        if not self.user:
            raise AuthError()
        return func(self, *args, **kwargs)

    return wrapper

class KanshinLoginBrowser(KanshinBrowser):
    def __init__(self, email, password, base_url='http://www.kanshin.com', cache=False):
        super(KanshinLoginBrowser, self).__init__(base_url, cache=False)

        self.login(email, password)

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

    @login_only
    def get_bookmarked_users(self):
        links = self.paginate_select('/home/bookmark?show=user', 'td.name a')

        return [{
            'id': int(link.get('href').split('/').pop()),
            'name': link.get_text()
        } for link in links]

    @login_only
    def get_bookmarked_keywords(self):
        links = self.paginate_select('/home/bookmark?show=keyword', 'td.name a')

        return [{
            'id': int(link.get('href').split('/').pop()),
            'title': link.get_text()
        } for link in links]

