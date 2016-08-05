import requests_cache
from kanshin.com.keyword import DetailPage as KeywordPage, ListPage as KeywordListPage
from kanshin.com.diary import DiaryPage

requests_cache.install_cache('test_cache')

def test_keyword():
    # 通常のキーワード
    kw = KeywordPage(2754133)

    assert kw.title == '鳥獣giga'
    assert kw.attributes == [
        {'name': '住所', 'value': '東京都世田谷区用賀４−３０−１０'},
        {'name': '電話番号', 'value': '03-6317-2017'},
        {'name': '営業時間', 'value': '火～金 12:00-13:30/17:00-23:30 土日 12:00-21:00 月曜定休'},
    ]



    # Amazon簡単キーワード商品
    kw = KeywordPage(2467663)

    assert kw.title == 'レボリューション・イン・ザ・バレー ―開発者が語るMacintosh誕生の舞台裏'
    assert kw.title_yomi == 'Revolution in The Valley'
    assert kw.text.find('QuickerGrafに関する記述') >= 0
    assert kw.created == '2010-08-31'
    assert kw.updated == '2010-08-31'
    assert kw.viewed > 3392
    assert kw.images == ['http://images-jp.amazon.com/images/P/4873112451.09._SCLZZZZZZZ_.jpg']

    assert kw.category == {'name':'書籍', 'id':101}
    assert kw.user == {'name': 'バスケ', 'id': 2}
    assert kw.attributes == [
        {'name': '商品名', 'value': 'レボリューション・イン・ザ・バレー ―開発者が語るMacintosh誕生の舞台裏'},
        {'name': '価格', 'value': '¥3,570'},
        {'name': '著者', 'value': 'Andy Hertzfeld'},
        {'name': '出版社', 'value': 'オライリージャパン'},
        {'name': '発売日', 'value': '2005-09-26'},
        {'name': 'URL', 'value': 'http://www.amazon.co.jp/exec/obidos/ASIN/4873112451/kanshin-1-22/ref=nosim'},
    ]

def test_diary():
    diary = DiaryPage(2922311)

    assert diary.title == 'デカワンコ'
    assert diary.text.find('綺麗に書いてあるなぁ。') >= 0
    assert diary.images == ['http://storage.kanshin.com/free/img_53/538430/k619183910.png']
    assert diary.date == '2010-12-13'
    assert diary.user == {'name': 'バスケ', 'id': 2}
