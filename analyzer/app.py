import connexion
from connexion import NoContent

import yaml
import json
import logging.config

from datetime import datetime as dt
from pykafka import KafkaClient

from os import path


with open("/app/conf/analyzer_config.yml", 'r') as f:
    app_config = yaml.safe_load(f.read())

with open("/app/conf/log_config.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    LOG_CONFIG["handlers"]["file"]["filename"] = "logs/analyzer.log"
    logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger('basicLogger')

stats_file_path = path.abspath(app_config['datastore']['filename'])
default_initial_state = app_config['schema']['stat']


def get_user_login_info(index):
    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode('events')]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    counter = 0
    for msg in consumer:
        message = msg.value.decode("utf-8")
        data = json.loads(message)
        logger.info("Message: %s" % msg)
    # Look for the index requested and return the payload with 200 status code
        payload = data["payload"]
        if data["type"] == "user_login":
            counter += 1
            if counter == index:
                return payload, 200
    return { "message": f"No message at index {index}!"}, 404

def get_player_performance(index):
    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode('events')]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    counter = 0
    for msg in consumer:
        message = msg.value.decode("utf-8")
        data = json.loads(message)
        logger.info("Message: %s" % msg)
    # Look for the index requested and return the payload with 200 status code
        payload = data["payload"]
        if data["type"] == "player_performance":
            counter += 1
            if counter == index:
                return payload, 200
    return { "message": f"No message at index {index}!"}, 404

import time
def get_stats():
    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode('events')]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    if path.exists(stats_file_path):
        with open(stats_file_path, "r") as fp:
            stats = json.load(fp)
    else:
        stats = {}

    stats["num_performance_report"] = 0
    stats["num_logins"] = 0
    for msg in consumer:
        message = msg.value.decode("utf-8")
        data = json.loads(message)
        logger.info("Message: %s" % msg)
        if data["type"] == "user_login":
            stats["num_logins"] += 1
        if data["type"] == "player_performance":
            stats["num_performance_report"] += 1
    
    logger.debug(f"Updated stats: {json.dumps(stats, indent=4)}")

    with open(stats_file_path, "w") as fp:
        json.dump(stats, fp, indent=4)

    logger.info("Beep boop! Updating completed. 🤖✅")
    if consumer:
        consumer.stop()
        time.sleep(0.5)
    return stats, 200

app = connexion.App(__name__, specification_dir='./')
app.add_api("openapi.yml",
            strict_validation=True,
            validate_responses=True
            )

if __name__ == '__main__':
    app.run(port=8111, host="0.0.0.0")
