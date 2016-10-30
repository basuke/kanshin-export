# -*- coding: utf-8 -*-

from kanshin.com.browser import *
from bs4 import BeautifulSoup
from bs4.element import Tag
from datetime import datetime
from kanshin.com import extract_text
import re


class KanshinGroupBrowser(KanshinBrowser):
    def __init__(self, group, base_url='http://www.kanshin.jp', cache=False):
    	base_url = base_url + '/' + group + '/'

        super(KanshinGroupBrowser, self).__init__(base_url, cache, parser='html.parser')

    def save_page(self):
    	pass

    def main_body(self):
    	s = BeautifulSoup(unicode(self.parsed), 'html5lib')
    	tags = [tag for tag in s.select('td') if tag.attrs.get('width') == '530']
    	return tags[0] if tags else None

    def login(self, email, password):
        self.logout()
        self.open('index.php3?mode=login')

        form = self.get_forms()[1]
        form['try_user'].value = email
        form['try_password'].value = password
        self.submit_form(form)

        if self.url.find('mode=home') < 0:
            raise "login unsuccessful"

        s = self.parsed

        uid = int(self.url.split('=').pop())
        self.user = {'id':uid, 'name':None}

    def logout(self):
        if self.user:
            self.open('cmd=logout')

            self.user = None

    @login_only
    def get_inbox(self):
    	for message in all_messages(self, 'index.php3?mode=message'):
    		yield message

    @login_only
    def get_outbox(self):
    	for message in all_messages(self, 'index.php3?mode=message&box=out'):
    		yield message

def is_tag(soup):
	return type(soup) == Tag

def tags(soup, name=None):
	return [tag for tag in soup.contents if is_tag(tag) and (name is None or tag.name == name)]

def filter_message_td(b):
	for tag in b.main_body().select('td'):
		if tag.attrs.get('bgcolor') != '#EEEEEE' and tag.attrs.get('align') != 'right':
			if len(tag.contents) > 1 or tag.contents[0].name != 'img':
				yield tag

def filter_messages_tds(b):
	tds = filter_message_td(b)
	tds.next()

	try:
		while True:
			yield (
				tds.next(),
				tds.next(),
				tds.next())
	except Exception as e:
		pass

def filter_messages(b):
	tds = filter_messages_tds(b)

	while True:
		col1, col2, col3 = tds.next()
		user = col1.select('b').pop().get_text()
		uid = col1.select('a').pop().get('href').split('=').pop()
		date = re.search('((\d+/)?(\d+)/(\d+) (\d+):(\d+) (am|pm))', str(col1))
		if date:
			y = date.group(2)
			m = int(date.group(3))
			d = int(date.group(4))
			h = int(date.group(5))
			min = int(date.group(6))
			ampm = date.group(7)

			if ampm == 'pm':
				h += 12

			if not y:
				y = '2016'
			else:
				y = '20' + y[0:-1]

			date = "%04d-%02d-%02d %02d:%02d:00" % (int(y), m, d, h, min)
			date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

		text = extract_text(col3.font.contents).replace(u'\n\n', u"\n")
		yield (
			uid,
			user,
			date,
			text)

def all_messages(b, url):
    page = 1

    while True:
    	b.open(url + '&page=%d' % (page))

        messages = list(filter_messages(b))
        if not messages:
        	break

    	for message in messages:
    		yield message

    	page += 1

def test(email, password):
	b = KimonoBrowser('kimono')
	b.login(email, password)

	print '====================================='
	for msg in b.get_outbox():
		print msg[0]
		print msg[1]
		print msg[2]
		print msg[3]
		print '====================================='

