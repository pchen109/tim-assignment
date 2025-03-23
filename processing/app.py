from os import path
from connexion import NoContent
from datetime import datetime as dt
from apscheduler.schedulers.background import BackgroundScheduler
import connexion
import yaml
import logging
import logging.config
import json
import httpx

conf_app_load = yaml.safe_load(open("/app/conf/processing_config.yml"))
stats_file_path = path.abspath(conf_app_load['datastore']['filename'])
# conf_log_path = path.abspath(conf_app_load['config']['conf_log_file'])
login_info_url = conf_app_load['eventstores']['login_info']['url']
performance_report_url = conf_app_load['eventstores']['performance_report']['url']
repeating_interval = conf_app_load['scheduler']['interval']
default_initial_state = conf_app_load['schema']['stat']

with open("/app/conf/log_config.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    LOG_CONFIG["handlers"]["file"]["filename"] = "logs/processing.log"
    logging.config.dictConfig(LOG_CONFIG)

logger = logging.getLogger('basicLogger')

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
        'interval',
        seconds = repeating_interval)
    sched.start()
    logger.info("Scheduler started!")

def populate_stats():
    logger.info("Beep boop! Updating data... 🤖")
    if path.exists(stats_file_path):
        with open(stats_file_path, "r") as fp:
            stats = json.load(fp)
    else:
        stats = default_initial_state
    
    start_timestamp = stats["last_updated"]
    end_timestamp = dt.now().strftime("%Y-%m-%dT%H:%M:%S-08:00")

    params = {
        'start_timestamp': start_timestamp,
        'end_timestamp': end_timestamp
    }

    login_events = event_logger(login_info_url, params, "login_info")
    performance_events = event_logger(performance_report_url, params, "performance_report")

    stats["num_logins"] += len(login_events)
    stats["max_login_streak"] = max(stats["max_login_streak"], new_record_value(login_events, "login_streak"))
    stats["num_performance_report"] += len(performance_events)
    stats["max_kills"] = max(stats["max_kills"], new_record_value(performance_events, "kills"))
    stats["last_updated"] = end_timestamp

    logger.debug(f"Updated stats: {json.dumps(stats, indent=4)}")

    # with open(stats_file_path, "w") as fp:
    #     json.dump(stats, fp, indent=4)
    with open("/app/data/output.json", "w") as fp:
        json.dump(stats, fp, indent=4)

    logger.info("Beep boop! Updating completed. 🤖✅")

def event_logger(url, params, event_type):
    # response = requests.get(url, params=params)
    response = httpx.get(url, params=params)
    events = response.json()

    if response.status_code == 200:
        logger.info(f"Received new {len(events)} events from {event_type}.")
    else:
        logger.error(f"Error fetching events from {url}: {response.status_code}")
    return events

def new_record_value(events, key):
    return max(events, key=lambda x: x[key], default={key: 0})[key]

def get_stats():
    logger.info("GET /stats request received.")

    if not path.exists(stats_file_path):
        logger.error("Statistics file not found.")
        return NoContent, 404

    with open(stats_file_path, "r") as file:
        stats = json.load(file) 
    
    logger.debug(f"Statistics: {json.dumps(stats, indent=4)}")
    logger.info("GET /stats request has completed successfully.")
    
    return [stats], 200

app = connexion.App(__name__, specification_dir='./')
app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True
            )

if __name__ == '__main__':
    init_scheduler()
    app.run(port=8100, host="0.0.0.0")