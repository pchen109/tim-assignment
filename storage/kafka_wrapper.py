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
        self.consumer = None
        self.connect()

    def connect(self):
        """Infinite loop: will keep trying"""
        while True:
            logger.debug("Trying to connect to Kafka...")
            if self.make_client():
                if self.make_consumer():
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
            self.consumer = None
            return False

    def make_consumer(self):
        """
        Runs once, makes a consumer and sets it on the instance.
        Returns: True (success), False (failure)
        """
        if self.consumer is not None:
            return True
        if self.client is None:
            return False
        try:
            topic = self.client.topics[self.topic]
            self.consumer = topic.get_simple_consumer(
                reset_offset_on_start=False,
                auto_offset_reset=OffsetType.LATEST
            )
        except KafkaException as e:
            msg = f"Make error when making consumer: {e}"
            logger.warning(msg)
            self.client = None
            self.consumer = None
            return False
        
    def commit(self):
        """Commit the offsets of the consumer"""
        if self.consumer is not None:
            self.consumer.commit_offsets()
            logger.debug("Offsets committed!")
        else:
            logger.warning("Consumer is None, cannot commit offsets.")
            
    def messages(self):
        """Generator method that catches exceptions in the consumer loop"""
        if self.consumer is None:
            self.connect()
        while True:
            try:
                for msg in self.consumer:
                    yield msg
            except KafkaException as e:
                msg = f"Kafka issue in comsumer: {e}"
                logger.warning(msg)
                self.client = None
                self.consumer = None
                self.connect()