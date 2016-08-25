import boto3
import logging
from inspect import getargspec


class Queue(object):
	def __init__(self, queue_name, region_name='us-west-1'):
		self.queue_name = queue_name

		self.logger = logging.getLogger('q:{}'.format(self.queue_name))
		self.logger.setLevel(logging.INFO)

		sqs = boto3.resource('sqs', region_name=region_name)
		self.queue = sqs.create_queue(QueueName=queue_name)

	def send(self, body):
		self.logger.info('<<< "{}"'.format(body))
		self.queue.send_message(MessageBody=u'{}'.format(body))

	def listen(self, task):
		self.logger.info('ready')

		args = []
		kwargs = {}

		spec = getargspec(task)

		if 'logger' in spec.args:
			kwargs['logger'] = self.logger

		if 'queue' in spec.args:
			kwargs['queue'] = self.queue

		need_message = ('message' in spec.args)

		while True:
			messages = self.queue.receive_messages(WaitTimeSeconds=20)

			for message in messages:
				self.logger.info('>>> "{}"'.format(message.body))

				if need_message:
					kwargs['message'] = self.logger

				try:
					task(message.body, **kwargs)
					message.delete()
				except Exception as e:
					self.logger.exception(self.queue_name)

