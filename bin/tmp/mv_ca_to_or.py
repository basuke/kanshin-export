#!/usr/bin/env python

import os.path
import sys

sys.path.insert(0, os.path.abspath('.'))

import boto3
from kanshin.data import has_image
from kanshin.com.export import is_imported

sqs_or = boto3.resource('sqs', region_name='us-west-2')

or_user_download = sqs_or.create_queue(QueueName='kanshin-com-user-download')
or_user_parse = sqs_or.create_queue(QueueName='kanshin-com-user-parse')
or_user_collect_keywords = sqs_or.create_queue(QueueName='kanshin-com-user-collect-keywords')
or_user_collect_diaries = sqs_or.create_queue(QueueName='kanshin-com-user-collect-diaries')
or_image_download = sqs_or.create_queue(QueueName='kanshin-com-image-download')
or_keyword_download = sqs_or.create_queue(QueueName='kanshin-com-keyword-download')
or_keyword_parse = sqs_or.create_queue(QueueName='kanshin-com-keyword-parse')
or_diary_download = sqs_or.create_queue(QueueName='kanshin-com-diary-download')
or_diary_parse = sqs_or.create_queue(QueueName='kanshin-com-diary-parse')

def copy(src, dest, filter_fn=None):
    for message in ls(src):
        if not filter_fn or filter_fn(message.body):
            send(dest, message.body)

            message.delete()

def ls(src, timeout=30):
    while True:
        messages = src.receive_messages(VisibilityTimeout=timeout, MaxNumberOfMessages=10)
        if not messages:
            break

        for message in messages:
            yield message

def send(q, body):
    q.send_message(MessageBody=body)


def echo(x):
    print(x)
    return True

def peek(src):
    return [m.body for m in ls(src, timeout=2)]
