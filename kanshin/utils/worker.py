import boto3
import logging

logger = logging.getLogger(__name__)

class Queue(object):
	def __init__(self, queue_name):
		self.queue_name = queue_name

		sqs = boto3.resource('sqs')
		self.queue = sqs.create_queue(QueueName=queue_name)

	def send(self, body):
		logger.info('q "{}" send "{}"'.format(self.queue_name, body))
		self.queue.send_message(MessageBody=u'{}'.format(body))

	def listen(self, task):
		logger.info('q "{}" ready'.format(self.queue_name))

		while True:
			messages = self.queue.receive_messages(WaitTimeSeconds=20)

			for message in messages:
				logger.info('q "{}" receive "{}"'.format(self.queue_name, message.body))

				try:
					task(message.body)
					message.delete()
				except Exception as e:
					logger.exception(self.queue_name)

