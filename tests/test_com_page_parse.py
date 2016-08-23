# -*- coding: utf-8 -*-

from kanshin.com.keyword import DetailPage as KeywordPage, ListPage as KeywordListPage
from kanshin.com.diary import DiaryPage
from bs4 import BeautifulSoup

def load(path):
    with open('tests/data/' + path) as f:
        return BeautifulSoup(f.read(), 'html.parser')


def test_keyword():
    """通常のキーワードページの解析"""
    kw = KeywordPage(2754133, load('keyword-2754133.html'))

    assert kw.title == u'鳥獣giga'
    assert kw.attributes == [
        {'name': u'住所', 'value': u'東京都世田谷区用賀４−３０−１０'},
        {'name': u'電話番号', 'value': u'03-6317-2017'},
        {'name': u'営業時間', 'value': u'火～金 12:00-13:30/17:00-23:30 土日 12:00-21:00 月曜定休'},
    ]


def test_keyword_amazon():
    """Amazon簡単キーワード商品ページの解析"""
    kw = KeywordPage(2467663, load('keyword-2467663.html'))

    assert kw.title == u'レボリューション・イン・ザ・バレー ―開発者が語るMacintosh誕生の舞台裏'
    assert kw.title_yomi == u'Revolution in The Valley'
    assert kw.text.find(u'QuickerGrafに関する記述') >= 0
    assert kw.created == u'2010-08-31'
    assert kw.updated == u'2010-08-31'
    assert kw.viewed > 3392
    assert kw.images == [u'http://images-jp.amazon.com/images/P/4873112451.09._SCLZZZZZZZ_.jpg']

    assert kw.category == {'name':u'書籍', 'id':101}
    assert kw.user == {'name': u'バスケ', 'id': 2}
    assert kw.attributes == [
        {'name': u'商品名', 'value': u'レボリューション・イン・ザ・バレー ―開発者が語るMacintosh誕生の舞台裏'},
        {'name': u'価格', 'value': u'¥3,570'},
        {'name': u'著者', 'value': u'Andy Hertzfeld'},
        {'name': u'出版社', 'value': u'オライリージャパン'},
        {'name': u'発売日', 'value': u'2005-09-26'},
        {'name': u'URL', 'value': u'http://www.amazon.co.jp/exec/obidos/ASIN/4873112451/kanshin-1-22/ref=nosim'},
    ]

    assert kw.comments[0]['user'] == u'Fuzzio'

def test_keyword_all_comments():
    """コメントがたくさんあるページの解析"""
    kw = KeywordPage(745093, load('keyword-745093.html'))
    assert kw.more_comments

    # コメント9件
    kw = KeywordPage(745093, load('keyword-745093-comment.html'))
    assert len(kw.comments) == 8

def test_keyword_all_connections():
    """リンクがたくさんあるページの解析"""
    kw = KeywordPage(218, load('keyword-218.html'))
    assert kw.more_connections

    # つながり30件
    kw = KeywordPage(218, load('keyword-218-connect.html'))
    assert len(kw.connections) == 30

def test_diary():
    """日記ページの解析"""
    diary = DiaryPage(2922311, load('diary-2922311.html'))

    assert diary.title == u'デカワンコ'
    assert diary.text.find(u'綺麗に書いてあるなぁ。') >= 0
    assert diary.images == [u'http://storage.kanshin.com/free/img_53/538430/k619183910.png']
    assert diary.date == u'2010-12-13'
    assert diary.user == {'name': u'バスケ', 'id': 2}

def test_sponsor():
    """スポンサーユーザー関係の解析"""
    diary = DiaryPage(1192187, load('diary-1192187.html'))

    assert diary.comments[-1]['sponsor'] == 'planted'
    assert diary.comments[-1]['user_id'] == 42756
