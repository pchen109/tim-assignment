import connexion
from connexion import NoContent

import yaml
import uuid
import json
import logging.config

from datetime import datetime as dt
from pykafka import KafkaClient

with open("/app/conf/receiver_config.yml", 'r') as f:
    app_config = yaml.safe_load(f.read())

with open("/app/conf/log_config.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    LOG_CONFIG["handlers"]["file"]["filename"] = "logs/receiver.log"
    logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger('basicLogger')

def report_event(body, event_type):
    trace_id = str(uuid.uuid4())
    body["trace_id"] = trace_id

    logger.info(f"Received event {event_type} with a trace id of {trace_id}")

    msg = {
        "type": event_type,
        "datetime": dt.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }

    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode('events')]
    producer = topic.get_sync_producer()
    producer.produce(json.dumps(msg).encode('utf-8'))

    logger.info(f"Response for event {event_type} (id: {trace_id}) has status 201")

    return NoContent, 201

def report_user_login_info(body):
    return report_event(body, "user_login")

def report_player_performance(body):
    return report_event(body, "player_performance")

app = connexion.App(__name__, specification_dir='./')
app.add_api("openapi.yml",
            strict_validation=True,
            validate_responses=True
            )

if __name__ == '__main__':
    app.run(port=8080, host="0.0.0.0")
