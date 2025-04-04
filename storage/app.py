from db import make_session
from models import LoginInfo, PerformanceReport

import connexion
from connexion import NoContent

import yaml
import logging
import logging.config

from datetime import datetime as dt
from sqlalchemy.sql import select
from threading import Thread

from pykafka import KafkaClient
from pykafka.common import OffsetType
import json

from kafka_wrapper import KafkaWrapper

with open("/app/conf/storage_config.yml", 'r') as f:
    app_config = yaml.safe_load(f.read())

with open("/app/conf/log_config.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    LOG_CONFIG["handlers"]["file"]["filename"] = "logs/storage.log"
    logging.config.dictConfig(LOG_CONFIG)

hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"

# client = KafkaClient(hosts=hostname)
# topic = client.topics[str.encode("events")]
# consumer = topic.get_simple_consumer(consumer_group=b'event_group',
#     reset_offset_on_start=False,
#     auto_offset_reset=OffsetType.LATEST
#     )

def process_messages():
    
    consumer = KafkaWrapper("kafka:9092", b"events")
    # Loop to consume messages and store them in the database
    for msg in consumer.messages():
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg["payload"]

        if msg["type"] == "user_login":
            report_user_login_info(payload)
        elif msg["type"] == "player_performance":
            report_player_performance(payload)

        consumer.consumer.commit_offsets()

def setup_kafka_thread():
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()

logger = logging.getLogger('basicLogger')

def get_event(db_model, start_timestamp, end_timestamp, log_message):
    session = make_session()

    ### accepts a string and returns a datetime object
    start = dt.fromisoformat(start_timestamp)
    end = dt.fromisoformat(end_timestamp)

    statement = select(db_model).where(db_model.date_created >= start).where(db_model.date_created < end)
    results = [result.to_dict() for result in session.execute(statement).scalars().all()]

    session.close()

    logger.info(log_message, len(results), start, end)
    return results

def get_user_login_info(start_timestamp, end_timestamp):
    return get_event(LoginInfo, start_timestamp, end_timestamp, "Found %d player login info (start: %s, end: %s)")

def get_player_performance(start_timestamp, end_timestamp):
    return get_event(PerformanceReport, start_timestamp, end_timestamp, "Found %d player performance (start: %s, end: %s)")

def report_user_login_info(body):
    user_id = body["user_id"]
    region = body["region"]
    login_streak = body["login_streak"]
    timestamp_str = body["timestamp"]
    timestamp = dt.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S%z")
    trace_id = body["trace_id"]

    session = make_session()

    event = LoginInfo(user_id, region, timestamp, login_streak, trace_id)

    session.add(event)
    session.commit()
    session.close()
    logger.debug(f"Stored event user_login with a trace id of {trace_id}")

    return NoContent, 201

def report_player_performance(body):
    user_id = body["user_id"]
    match_id = body["match_id"]
    kills = body["kills"]
    deaths = body["deaths"]
    assists = body["assists"]
    game_length = body["game_length"]
    timestamp_str = body["timestamp"]
    timestamp = dt.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S%z")
    trace_id = body["trace_id"]

    session = make_session()

    event = PerformanceReport(user_id, match_id, kills, deaths, assists, game_length, timestamp, trace_id)

    session.add(event)
    session.commit()
    session.close()

    logger.debug(f"Stored event performance with a trace id of {trace_id}")

    return NoContent, 201


### Assignment - Get the number of records ###################################
def get_record_numbers():
    session = make_session()
    login_counts = session.query(LoginInfo).count()
    performance_counts = session.query(PerformanceReport).count()
    session.close()

    return {
        "login_counts": login_counts,
        "performance_counts": performance_counts
    }
##############################################################################

### Assignment - Get IDS #####################################################
def get_ids(table, event_type):
    session = make_session()
    id_name = [id_name[0] for id_name in session.query(table.trace_id).all()]
    trace_id = [trace_id[0] for trace_id in session.query(table.trace_id).all()]
    session.close()

    list_of_ids = [{"event_id": id_name[i], "trace_id": trace_id[i], "event_type": event_type} for i in range(len(id_name))]
    return list_of_ids, 200
# def get_login_ids():
#     session = make_session()
#     id_name = [id_name[0] for id_name in session.query(LoginInfo.trace_id).all()]
#     trace_id = [trace_id[0] for trace_id in session.query(LoginInfo.trace_id).all()]
#     session.close()

#     list_of_ids = [{"user_id": id_name[i], "trace_id": trace_id[i]} for i in range(len(id_name))]
#     return list_of_ids, 200

def get_login_ids():
    return get_ids(LoginInfo, "login")
def get_performacne_ids():
    return get_ids(PerformanceReport, "player_performance")
##############################################################################

app = connexion.App(__name__, specification_dir='./')
app.add_api("openapi.yml",
            base_path="/storage",
            strict_validation=True,
            validate_responses=True
            )
from db_management import create_tables_if_not_exist
if __name__ == '__main__':
    create_tables_if_not_exist()
    setup_kafka_thread()
    app.run(port=8090, host="0.0.0.0")