#!/usr/bin/env python

import os.path
import sys

sys.path.insert(0, os.path.abspath('.'))

import boto3
from kanshin.data import has_image
from kanshin.com.export import is_imported

sqs_ca = boto3.resource('sqs', region_name='us-west-1')
sqs_or = boto3.resource('sqs', region_name='us-west-2')

ca_user_download = sqs_ca.create_queue(QueueName='kanshin-com-user-download')
ca_user_parse = sqs_ca.create_queue(QueueName='kanshin-com-user-parse')
ca_user_collect_keywords = sqs_ca.create_queue(QueueName='kanshin-com-user-collect-keywords')
ca_user_collect_diaries = sqs_ca.create_queue(QueueName='kanshin-com-user-collect-diaries')
ca_image_download = sqs_ca.create_queue(QueueName='kanshin-com-image-download')
ca_keyword_download = sqs_ca.create_queue(QueueName='kanshin-com-keyword-download')
ca_keyword_parse = sqs_ca.create_queue(QueueName='kanshin-com-keyword-parse')
ca_diary_download = sqs_ca.create_queue(QueueName='kanshin-com-diary-download')
ca_diary_parse = sqs_ca.create_queue(QueueName='kanshin-com-diary-parse')

or_user_download = sqs_or.create_queue(QueueName='kanshin-com-user-download')
or_user_parse = sqs_or.create_queue(QueueName='kanshin-com-user-parse')
or_user_collect_keywords = sqs_or.create_queue(QueueName='kanshin-com-user-collect-keywords')
or_user_collect_diaries = sqs_or.create_queue(QueueName='kanshin-com-user-collect-diaries')
or_image_download = sqs_or.create_queue(QueueName='kanshin-com-image-download')
or_keyword_download = sqs_or.create_queue(QueueName='kanshin-com-keyword-download')
or_keyword_parse = sqs_or.create_queue(QueueName='kanshin-com-keyword-parse')
or_diary_download = sqs_or.create_queue(QueueName='kanshin-com-diary-download')
or_diary_parse = sqs_or.create_queue(QueueName='kanshin-com-diary-parse')

t1 = sqs_or.create_queue(QueueName='test1')
t2 = sqs_or.create_queue(QueueName='test2')

def copy(src, dest, filter_fn=None):
    for message in ls(src):
        if not filter_fn or filter_fn(message.body):
            send(dest, message.body)
            message.delete()

def ls(src):
    while True:
        messages = src.receive_messages(VisibilityTimeout=1, MaxNumberOfMessages=10)
        if not messages:
            break

        for message in messages:
            yield message

def send(q, body):
    q.send_message(MessageBody=body)


def echo(x):
    print(x)
    return True

