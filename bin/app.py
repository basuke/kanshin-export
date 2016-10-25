# -*- coding: utf-8 -*-

import os.path
import sys
sys.path.insert(0, os.path.abspath('.'))

from bottle import route, run, template, request, response, redirect
from kanshin.data import fetch_user_diaries, fetch_user_keywords
from kanshin.export import build_mt_entry, convert_keyword_to_diary


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


@route('/user/<user_id:int>')
def redirect_user(user_id):
    redirect('http://www.kanshin.com/user/{user_id}'.format(user_id=user_id))


port = sys.argv[1] if len(sys.argv) > 1 else 8050
run(host='0.0.0.0', port=port, server='gunicorn')
