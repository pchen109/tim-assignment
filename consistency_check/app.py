from os import path, environ
from connexion import NoContent
from datetime import datetime as dt
from apscheduler.schedulers.background import BackgroundScheduler
import connexion
import yaml
import logging
import logging.config
import json
from pykafka import KafkaClient
import httpx
import json
from datetime import datetime as dt
import math
import time

with open("/app/conf/log_config.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    LOG_CONFIG["handlers"]["file"]["filename"] = "logs/consistency_check.log"
    logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger('basicLogger')

with open("/app/conf/consistency_check_config.yml", 'r') as f:
    app_config = yaml.safe_load(f.read())

### POST w/o no extra body 
def run_consistency_checks():
    time_start = time.time()
    logger.info("Consistency checks starts ... 💀")
    processing_json = httpx.get("http://processing:8100/processing/stats").json()
    
    queue_counts_json = httpx.get("http://analyzer:8111/analyzer/stats").json()
    queue_login_ids_json = httpx.get("http://analyzer:8111/analyzer/login_ids").json()
    queue_perf_ids_json = httpx.get("http://analyzer:8111/analyzer/performance_ids").json()
    
    db_counts_json = httpx.get("http://storage:8090/storage/records").json()
    db_login_ids_json = httpx.get("http://storage:8090/storage/login_ids").json()
    db_perf_ids_json = httpx.get("http://storage:8090/storage/performance_ids").json()

    events_missing_in_queue = []
    events_missing_in_db = []

    logger.info(f"{'=' * 99}{queue_login_ids_json}")
    processing_counts_json = {
        "login_counts": processing_json[0]["login_counts"],
        "performance_counts": processing_json[0]["performance_counts"]
    }


    for id_queue in queue_login_ids_json:
        if not any(id_queue["trace_id"] == id_sto["trace_id"] for id_sto in db_login_ids_json):
            events_missing_in_db.append(id_queue)

    for id_queue in queue_perf_ids_json:
        if not any(id_queue["trace_id"] == id_sto["trace_id"] for id_sto in db_perf_ids_json):
            events_missing_in_db.append(id_queue)
    
    for id_sto in db_login_ids_json:
        if not any(id_sto["trace_id"] == id_queue["trace_id"] for id_queue in queue_login_ids_json):
            events_missing_in_queue.append(id_sto)

    for id_sto in db_perf_ids_json:
        if not any(id_sto["trace_id"] == id_queue["trace_id"] for id_queue in queue_perf_ids_json):
            events_missing_in_queue.append(id_sto)

    output = {
        "last_updated": "2025-03-15T14:30:00Z",
        "counts": {
            "db": db_counts_json,
            "queue": queue_counts_json,
            "processing": processing_counts_json,
        },
        "missing_in_db": events_missing_in_db,
        "missing_in_queue": events_missing_in_queue,
    }

    with open("/app/data/consistency_check/output.json", "w") as fp:
        json.dump(output, fp, indent=4)

    processing_time_ms = math.ceil((time.time() - time_start) * 1000)
    logger.info(f"""Consistency checks completed |
        Processing Time (ms): {processing_time_ms} |
        Missing in DB: {len(events_missing_in_db)} |
        Missing in Queue: {len(events_missing_in_queue)} 
        👻🦉🐢""")

    return {"processing_time_ms": processing_time_ms}

def get_checks():
    if not path.exists("/app/data/consistency_check/output.json") or path.getsize("/app/data/consistency_check/output.json") == 0:
        return {"error": "no check has been run yet"}, 404

    with open("/app/data/consistency_check/output.json", "r") as fp:
        response = json.load(fp)

    if "last_updated" not in response:
        return {"error": "no check or check has issue"}, 404
    
    return response, 200

app = connexion.App(__name__, specification_dir='./')
app.add_api("consistency_check.yaml",
            base_path="/consistency_check",
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
    app.run(port=7777, host="0.0.0.0")