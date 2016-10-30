# -*- coding: utf-8 -*-

import os.path
import sys
sys.path.insert(0, os.path.abspath('.'))

from bottle import route, run, template, request, response, redirect
from kanshin.data import fetch_user_diaries, fetch_user_keywords
from kanshin.export import build_mt_entry, convert_keyword_to_diary, build_message_body
from kanshin.jp.browser import KanshinGroupBrowser


@route('/_/export/diary/mt/<user_id:int>')
def export_diary(user_id):
    filename = 'kanshin-diary-{user_id}.txt'.format(user_id=user_id)

    response.set_header('Content-Description', 'File Transfer')
    response.set_header('Content-Type', 'application/octet-stream')
    response.set_header('Content-Disposition', 'attachment; filename=' + filename);
    response.set_header('Content-Transfer-Encoding', 'binary')

    for item in fetch_user_diaries(user_id):
        yield build_mt_entry(options=request.query, **item)


@route('/_/export/keyword/mt/<user_id:int>')
def export_keyword(user_id):
    filename = 'kanshin-keyword-{user_id}.txt'.format(user_id=user_id)

    response.set_header('Content-Description', 'File Transfer')
    response.set_header('Content-Type', 'application/octet-stream')
    response.set_header('Content-Disposition', 'attachment; filename=' + filename);
    response.set_header('Content-Transfer-Encoding', 'binary')

    for item in fetch_user_keywords(user_id):
        item = convert_keyword_to_diary(item)
        yield build_mt_entry(options=request.query, **item)


@route('/_/export/message/')
def export_group_messages_form():
	return """
	<h1>関心空間グループ 伝言ダウンロードサービス</h1>

	<form action="/_/export/message/download" method="GET">
		<dl>
			<dt><label for="group">グループ</label></dt>
			<dd><input id="group" name="group" size="20" value="kimono"></dd>

			<dt><label for="email">e-mail</label></dt>
			<dd><input id="email" name="email" size="60"></dd>

			<dt><label for="password">パスワード</label></dt>
			<dd><input id="password" type="password" name="password" size="20"></dd>

			<dt><input name="download" type="submit" value="download"></dt>
		</dl>
	</form>
	"""

@route('/_/export/message/download')
def export_group_messages():
    group = request.GET.group
    email = request.GET.email
    password = request.GET.password

    b = KanshinGroupBrowser(group)
    b.login(email, password)

    filename = '{group}-message-{email}.html'.format(email=email, group=group)

    response.set_header('Content-Description', 'File Transfer')
    response.set_header('Content-Type', 'application/octet-stream')
    response.set_header('Content-Disposition', 'attachment; filename=' + filename);
    response.set_header('Content-Transfer-Encoding', 'binary')

    yield u"""<style>
    .in a, .out a, date {
    	font-weight: bold;
    }
    """

    yield u"<h2>自分へ届いた伝言</h2>\n<hr>"
    for msg in b.get_inbox():
        yield build_message_body(msg[0], msg[1], msg[2], msg[3], False)

    yield u"<h2>自分が出した伝言</h2>\n<hr>"
    for msg in b.get_outbox():
        yield build_message_body(msg[0], msg[1], msg[2], msg[3], True)


@route('/user/<user_id:int>')
def redirect_user(user_id):
    redirect('http://www.kanshin.com/user/{user_id}'.format(user_id=user_id))


port = sys.argv[1] if len(sys.argv) > 1 else 8050
run(host='0.0.0.0', port=port, server='gunicorn', timeout=60*10)
