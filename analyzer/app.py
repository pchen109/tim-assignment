import logging.config
import yaml
import json
import connexion
from connexion import NoContent
from pykafka import KafkaClient
from os import path, environ

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
        logger.info(f"WHOLE MESSAGE: {data}")
        logger.info("Age: %s" % msg)
        print(f"WHOLE MESSAGE: {data}")
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

    stats = {}
    stats["performance_counts"] = 0
    stats["login_counts"] = 0
    logger.debug(f"Updated stats: {json.dumps(stats, indent=4)}")
    
    for msg in consumer:
        message = msg.value.decode("utf-8")
        data = json.loads(message)
        logger.info("Message: %s" % msg)
        if data["type"] == "user_login":
            stats["login_counts"] += 1
        if data["type"] == "player_performance":
            stats["performance_counts"] += 1
    
    logger.debug(f"Updated stats: {json.dumps(stats, indent=4)}")

    logger.info("Beep boop! Updating completed. 🤖✅")
    if consumer:
        consumer.stop()
        time.sleep(0.5)
    return stats, 200

app = connexion.App(__name__, specification_dir='./')
app.add_api("openapi.yml",
            base_path="/analyzer",
            strict_validation=True,
            validate_responses=True
            )

from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware

if "CORS_ALLOW_ALL" in environ and environ["CORS_ALLOW_ALL"] == "yes":
    app.add_middleware(
        CORSMiddleware,
        position=MiddlewarePosition.BEFORE_EXCEPTION,
        allow_origins=["*"],  # Allows all origins (INSECURE for production!)
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

### Assignment - Get IDS #####################################################
def get_ids(type, id_name):
    client = KafkaClient(hosts="kafka:9092")
    topic = client.topics[str.encode('events')]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    ids = []
    for bin in consumer:
        msg = bin.value.decode("utf-8")
        data = json.loads(msg)

        if data["type"] == type:
            ids.append({
                "event_id": data["payload"][id_name],
                "trace_id": data["payload"]["trace_id"],
                "event_type": type
            })
    
    return ids, 200
def get_login_ids():
    return get_ids("user_login", "user_id")
def get_performacne_ids():
    return get_ids("player_performance", "match_id")
##############################################################################

if __name__ == '__main__':
    app.run(port=8111, host="0.0.0.0")
