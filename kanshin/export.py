# -*- coding: utf-8 -*-

import re


URL_PATTERN = re.compile(r"\[(.+?)\]\((https?://.+?)\)")

IMG_TEMPLATE = u'<div><img src="{url}" class="kanshin-entry-images"></div>'
LINK_TEMPLATE = u'<a href="{url}" class="kanshin-link">{title}</a>'

COMMENT_TEMPLATE = u'''-----
COMMENT:
AUTHOR: {user}
URL: http://www.kanshin.link/user/{id}
DATE: {date}
{text}
'''

ENTRY_TEMPLATE = u'''TITLE: {title}
BASENAME: {kind}-{id}
AUTHOR: {user}
DATE: {date}
CONVERT BREAKS: 0
CATEGORY: {category}
STATUS: publish
ALLOW COMMENTS: 1
ALLOW PING: 0
-----
BODY:
{text}
-----
--------
'''

INBOX_TEMPLATE = u"""
<div class="date">{date}</div>
<div class="in"><a href="http://potomak.com/kimono/index.php3-mode=home&id={uid}.html">{user}</a>さんから伝言</div>
<p>{text}</p>
<hr>
"""

OUTBOX_TEMPLATE = u"""
<div class="date">{date}</div>
<div class="out"><a href="http://potomak.com/kimono/index.php3-mode=home&id={uid}.html">{user}</a>さんへの伝言</div>
<p>{text}</p>
<hr>
"""



def convert_link(m):
    title = m.group(1)
    url = m.group(2)
    return LINK_TEMPLATE.format(title=title, url=url)


def convert_to_mt_date(date, hour=u'08', min=u'00', sec=u'00'):
    year, month, day = date.split(u'-')
    return u'{month}/{day}/{year} {hour}:{min}:{sec}'.format(
        year=year,
        month=month,
        day=day,
        hour=hour,
        min=min,
        sec=sec
    )


def convert_text_entry(text):
    return URL_PATTERN.sub(convert_link, text).replace('\n', '<br>\n')


def build_mt_entry(id, kind, category, 
    title, date, text, images, user, comments, 
    options={}, **kwargs):
    text = convert_text_entry(text)

    if images:
        images = u"\n".join([IMG_TEMPLATE.format(url=url) for url in images])

        # if options.image_location == 'bottom':
        #     text = text + "\n\n" + images
        # else:
        text = images + u"\n\n" + text

    if comments:
        text += u"\n" + u"".join([COMMENT_TEMPLATE.format(
            user=comment['user'],
            id=comment['user_id'],
            date=convert_to_mt_date(comment['date']),
            text=convert_text_entry(comment['text'].strip())
        ) for comment in comments]).strip()

    return ENTRY_TEMPLATE.format(
        id=id,
        kind=kind,
        user=user,
        text=text,
        title=title,
        date=convert_to_mt_date(date),
        category=category
    )

def convert_keyword_to_diary(kw):
    text = kw['text']

    if kw['attributes']:
        attr_box = u'<dl class="attributes">'
        for attr in kw['attributes']:
            attr_box += u'<dt>{name}</dt><dd>{value}</dd>'.format(**attr)
        attr_box += u'</dl>'

        text += attr_box

    return {
        'id': kw['id'],
        'user': kw['user'],
        'text': text,
        'title': kw['title'],
        'date': kw['created'],
        'category': kw['category']['name'],

        'images': kw['images'],
        'comments': kw['comments'],
    }

def build_message_body(id, name, date, text, out):
    template = OUTBOX_TEMPLATE if out else INBOX_TEMPLATE
    return template.format(uid=id, user=name, date=date, text=text.replace(u'\n', u'<br>\n'))

