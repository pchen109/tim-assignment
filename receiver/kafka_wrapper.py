import time
import random
import logging
import logging.config   
from pykafka import KafkaClient
from pykafka.exceptions import KafkaException
from pykafka.common import OffsetType

# Configure logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class KafkaWrapper:
    def __init__(self, hostname, topic):
        self.hostname = hostname
        self.topic = topic
        self.client = None
        self.producer = None
        self.connect()
    def connect(self):
        """Infinite loop: will keep trying"""
        while True:
            logger.debug("Trying to connect to Kafka...")
            if self.make_client():
                if self.make_producer():
                    break
        # Sleeps for a random amount of time (0.5 to 1.5s)
        time.sleep(random.randint(500, 1500) / 1000)

    def make_client(self):
        """
        Runs once, makes a client and sets it on the instance.
        Returns: True (success), False (failure)
        """
        if self.client is not None:
            return True
        try:
            self.client = KafkaClient(hosts=self.hostname)
            logger.info("Kafka client created!")
            return True
        except KafkaException as e:
            msg = f"Kafka error when making client: {e}"
            logger.warning(msg)
            self.client = None
            self.producer = None
            return False

    def make_producer(self):
        """
        Runs once, makes a producer and sets it on the instance.
        Returns: True (success), False (failure)
        """
        if self.producer is not None:
            return True
        if self.client is None:
            return False
        try:
            topic = self.client.topics[self.topic]
            self.producer = topic.get_sync_producer()
        except KafkaException as e:
            msg = f"Make error when making producer: {e}"
            logger.warning(msg)
            self.client = None
            self.producer = None
            return False
        
    def produce(self, message):
        """Generator method that catches exceptions in the producer loop"""
        if self.producer is None:
            self.connect()
        while True:
            if self.producer is None:
                logger.error("Producer not initialized")
                return
            try:
                # Check if the message is a string, and if so, encode it
                if isinstance(message, str):
                    message = message.encode('utf-8')
                # Now, message is guaranteed to be in bytes
                self.producer.produce(message)
                logger.info("Message produced successfully")
            except KafkaException as e:
                msg = f"Error occurred while producing message: {e}"
                logger.error(msg)
                self.client = None  # Optionally reset client if necessary
                self.producer = None  # Reset producer in case of error
                self.connect() 