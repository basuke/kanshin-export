# -*- coding: utf-8 -*-

import re


URL_PATTERN = re.compile(r"\[(.+?)\]\((https?://.+?)\)")

IMG_TEMPLATE = u'<img src="{url}" class="kanshin-diary-entry-images">'
LINK_TEMPLATE = u'<a href="{url}" class="kanshin-link">{title}</a>'

COMMENT_TEMPLATE = u'''-----
COMMENT:
AUTHOR: {user}
URL: http://www.kanshin.link/user/{id}
DATE: {date}
{text}
'''

ENTRY_TEMPLATE = u'''TITLE: {title}
BASENAME: diary-{id}
AUTHOR: {user}
DATE: {date}
CONVERT BREAKS: 1
CATEGORY: {category}
-----
BODY:
{text}
-----
--------
'''


def _convert_markdown_link(m):
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
    return URL_PATTERN.sub(_convert_markdown_link, text)


def build_mt_entry(id, title, date, text, images, user, comments, options={}, **kwargs):
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
        user=user,
        text=text,
        title=title,
        date=convert_to_mt_date(date),
        category=u'関心空間の日記'
    )

