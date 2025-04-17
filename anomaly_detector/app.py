import logging.config
import yaml
import json
import connexion
from connexion import NoContent
from pykafka import KafkaClient
from os import path, environ
import time
import math


with open("/app/conf/analyzer_config.yml", 'r') as f:
    app_config = yaml.safe_load(f.read())

with open("/app/conf/log_config.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    LOG_CONFIG["handlers"]["file"]["filename"] = "logs/anomaly_detector.log"
    logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger('basicLogger')

stats_file_path = path.abspath(app_config['datastore']['filename'])
default_initial_state = app_config['schema']['stat']

def update_anomalies():
    time_start = time.time()
    logger.debug(f"Updated anomalies service")
    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode('events')]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    stats = {}
    stats["kills_anomalies"] = 0
    stats["login_streak_anomalies"] = 0
    
    for msg in consumer:
        message = msg.value.decode("utf-8")
        data = json.loads(message)
        payload = data["payload"]

        if data["type"] == "user_login":
            if payload["login_streak"] >= 30:
                logger.info(f"Message: detect values {payload["login_streak"]} larger than 30")
                stats["login_streak_anomalies"] += 1
        if data["type"] == "player_performance":
            if payload["kills"] >= 20:
                logger.info(f"Message: detect values {payload["kills"]} larger than 20")
                stats["kills_anomalies"] += 1
    
    with open("/app/data/anomaly_detector/output.json", "w") as fp:
        json.dump(stats, fp, indent=4)
    logger.debug(f"Updated stats: {json.dumps(stats, indent=4)}")

    logger.info("Beep boop! Updating completed. 🤖✅")
    if consumer:
        consumer.stop()
        time.sleep(0.5)
    
    processing_time_ms = math.ceil((time.time() - time_start) * 1000)
    logger.info(f"""anomalies checks completed |
        Processing Time (ms): {processing_time_ms} |
        👻🦉🐢""")
    return stats, 200




# def get_anomalies(event_type):
#     client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
#     topic = client.topics[str.encode('events')]
#     consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

#     counter = 0
#     for msg in consumer:
#         message = msg.value.decode("utf-8")
#         data = json.loads(message)
#         logger.info(f"WHOLE MESSAGE: {data}")
#         logger.info("Age: %s" % msg)
#         payload = data["payload"]
#         if data["type"] == event_type:
#             counter += 1
#             if payload["login_streak"] >= 30:
#     return None


app = connexion.App(__name__, specification_dir='./')
app.add_api("openapi.yml",
            base_path="/anomaly_detector",
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

if __name__ == '__main__':
    logger.info("Message: anomaly service will detect all player performance where the kills are above 20. It will also detect max login streak where the number is higher than 30.")
    app.run(port=8222, host="0.0.0.0")
