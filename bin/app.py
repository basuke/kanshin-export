# -*- coding: utf-8 -*-

import os.path
import sys
sys.path.insert(0, os.path.abspath('.'))

from bottle import route, run, template, request, response, redirect
from kanshin.data import fetch_user_diaries
from kanshin.export import build_mt_entry

@route('/_/export/diary/mt/<user_id:int>')
def export_diary(user_id):
    filename = 'kanshin-diary-{user_id}.txt'.format(user_id=user_id)

    response.set_header('Content-Description', 'File Transfer')
    response.set_header('Content-Type', 'application/octet-stream')
    response.set_header('Content-Disposition', 'attachment; filename=' + filename);
    response.set_header('Content-Transfer-Encoding', 'binary')

    result = fetch_user_diaries(user_id)

    for item in result:
        yield build_mt_entry(options=request.query, **item)

@route('/user/<user_id:int>')
def redirect_user(user_id):
    redirect('http://www.kanshin.com/user/{user_id}'.format(user_id=user_id))

port = sys.argv[1] if len(sys.argv) > 1 else 8080
run(host='0.0.0.0', port=port, server='gunicorn')
