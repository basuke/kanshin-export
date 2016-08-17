# -*- coding: utf-8 -*-

import os.path
import sys
sys.path.insert(0, os.path.abspath('.'))

from bottle import route, run, template, request, response, redirect
import boto3
from boto3.dynamodb.conditions import Key
from kanshin.data import fetch_user_diaries


IMG_TEMPLATE = '<img src="{url}" class="kanshin-diary-entry-images">'

COMMENT_TEMPLATE = '''-----
COMMENT:
AUTHOR: {user}
URL: http://www.kanshin.link/user/{id}
DATE: {date}
{text}
'''

ENTRY_TEMPLATE = '''TITLE: {title}
BASENAME: diary-{id}
AUTHOR: {user}
DATE: {date}
CONVERT BREAKS: markdown_with_smartypants
CATEGORY: {category}
-----
BODY:
{text}
-----
--------
'''


def convert_date(date, hour='08', min='00', sec='00'):
    year, month, day = date.split('-')
    return '{month}/{day}/{year} {hour}:{min}:{sec}'.format(
        year=year,
        month=month,
        day=day,
        hour=hour,
        min=min,
        sec=sec
    )

def build_entry(id, title, date, text, images, user, comments, options={}, **kwargs):
    if images:
        images = "\n".join([IMG_TEMPLATE.format(url=url) for url in images])

        # if options.image_location == 'bottom':
        #     text = text + "\n\n" + images
        # else:
        text = images + "\n\n" + text

    if comments:
        text += "\n" + "".join([COMMENT_TEMPLATE.format(
            user=comment['user'],
            id=comment['user_id'],
            date=convert_date(comment['date']),
            text=comment['text'].strip()
        ) for comment in comments]).strip()

    return ENTRY_TEMPLATE.format(
        id=id,
        user=user,
        text=text,
        title=title,
        date=convert_date(date),
        category='関心空間の日記'
    )

@route('/_/export/diary/mt/<user_id:int>')
def export_diary(user_id):
    filename = 'kanshin-diary-{user_id}.txt'.format(user_id=user_id)

    response.set_header('Content-Description', 'File Transfer')
    response.set_header('Content-Type', 'application/octet-stream')
    response.set_header('Content-Disposition', 'attachment; filename=' + filename);
    response.set_header('Content-Transfer-Encoding', 'binary')

    result = fetch_user_diaries(user_id)

    for item in result:
        yield build_entry(options=request.query, **item)

@route('/user/<user_id:int>')
def redirect_user(user_id):
    redirect('http://www.kanshin.com/user/{user_id}'.format(user_id=user_id))

port = sys.argv[1] if len(sys.argv) > 1 else 8080
run(host='0.0.0.0', port=port, server='gunicorn')
