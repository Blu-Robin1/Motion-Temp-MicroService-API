from pykafka import KafkaClient
from pykafka.exceptions import KafkaException
from pykafka.common import OffsetType
import json
import logging
import time
import random

logger = logging.getLogger(__name__)


class KafkaWrapper:
    def __init__(self, hostname, topic):
        self.hostname = hostname
        self.topic_name = topic

        self.client = None
        self.consumer = None
        self.producer = None

        self.connect()

    def connect(self):
        """Keep trying until everything is ready"""
        while True:
            logger.debug("Trying to connect to Kafka...")

            if self.make_client():
                if self.make_consumer() and self.make_producer():
                    break

            time.sleep(random.randint(500, 1500) / 1000)

    def make_client(self):
        if self.client is not None:
            return True

        try:
            self.client = KafkaClient(hosts=self.hostname)
            logger.info("Kafka client created!")
            return True
        except KafkaException as e:
            logger.warning(f"Kafka client error: {e}")
            self.reset()
            return False

    def make_consumer(self):
        if self.consumer is not None:
            return True
        if self.client is None:
            return False

        try:
            topic = self.client.topics[self.topic_name]
            self.consumer = topic.get_simple_consumer(
                reset_offset_on_start=False,
                auto_offset_reset=OffsetType.LATEST
            )
            logger.info("Kafka consumer created!")
            return True
        except KafkaException as e:
            logger.warning(f"Consumer error: {e}")
            self.reset()
            return False

    def make_producer(self):
        if self.producer is not None:
            return True
        if self.client is None:
            return False

        try:
            topic = self.client.topics[self.topic_name]
            self.producer = topic.get_sync_producer()
            logger.info("Kafka producer created!")
            return True
        except KafkaException as e:
            logger.warning(f"Producer error: {e}")
            self.reset()
            return False

    def reset(self):
        self.client = None
        self.consumer = None
        self.producer = None

    # -------------------------
    # CONSUMER
    # -------------------------
    def messages(self):
        if self.consumer is None:
            self.connect()

        while True:
            try:
                for msg in self.consumer:
                    yield msg
            except KafkaException as e:
                logger.warning(f"Consumer loop error: {e}")
                self.reset()
                self.connect()

    # -------------------------
    # PRODUCER
    # -------------------------
    def produce(self, message: dict):
        """Send a JSON message to Kafka"""
        if self.producer is None:
            self.connect()

        try:
            msg_bytes = json.dumps(message).encode("utf-8")
            self.producer.produce(msg_bytes)
        except KafkaException as e:
            logger.warning(f"Producer send error: {e}")
            self.reset()
            self.connect()