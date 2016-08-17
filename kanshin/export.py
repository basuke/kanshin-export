# -*- coding: utf-8 -*-

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


def convert_to_mt_date(date, hour='08', min='00', sec='00'):
    """
    convert '2016-08-10' style date string into MT date format
    >>> convert_to_mt_date('2016-08-10')
    '08/10/2016 08:00:00'
    """
    year, month, day = date.split('-')
    return '{month}/{day}/{year} {hour}:{min}:{sec}'.format(
        year=year,
        month=month,
        day=day,
        hour=hour,
        min=min,
        sec=sec
    )

def build_mt_entry(id, title, date, text, images, user, comments, options={}, **kwargs):
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
            date=convert_to_mt_date(comment['date']),
            text=comment['text'].strip()
        ) for comment in comments]).strip()

    return ENTRY_TEMPLATE.format(
        id=id,
        user=user,
        text=text,
        title=title,
        date=convert_to_mt_date(date),
        category='関心空間の日記'
    )

