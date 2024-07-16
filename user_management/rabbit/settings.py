import json
from datetime import datetime
from typing import Dict

import pika
import pytz
from pika.exceptions import AMQPConnectionError

from user_management.config import config
from user_management.logger_settings import logger


class PikaClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.host = config.RABBITMQ_HOST
        self.port = config.RABBITMQ_PORT

    def connect(self):
        credentials = pika.PlainCredentials(config.RABBITMQ_USERNAME, config.RABBITMQ_PASSWORD)
        parameters = pika.ConnectionParameters(self.host, self.port, "/", credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def create_queue(self, queue_name):
        self.channel.queue_declare(queue=queue_name)

    def close_connection(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

    def publish_message(self, email: str, reset_url: str, queue_name: str):
        try:
            self.connect()
            self.create_queue(queue_name)

            properties: pika.BasicProperties = pika.BasicProperties(headers={"email": f"{email}"})
            body: Dict = {
                "reset_url": reset_url,
                "publish_datetime": datetime.now(tz=pytz.timezone(config.TIMEZONE)).isoformat(),
            }
            self.channel.basic_publish(
                exchange="", routing_key=queue_name, body=json.dumps(body), properties=properties
            )
        except AMQPConnectionError as e:
            logger.error(e)

        finally:
            self.close_connection()
