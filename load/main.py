import threading
import uvicorn

from fastapi import FastAPI
from load.utils_trainer import execute_data_collection
from apscheduler.schedulers.blocking import BlockingScheduler
from utils.params_config import loader_fast_api_port, loader_fast_api_host, LOADER_MINUTES_OFFSET
app = FastAPI()
scheduler = BlockingScheduler()
collect_data_status = True

@app.get("/collect_data/status")
def collect_data_status():
    return {
        "collect_data_status": collect_data_status,
        "minutes_offset": LOADER_MINUTES_OFFSET
    }

@app.post("/collect_data/activate")
def toogle_collect_data():
    collect_data_status = True
    return {
        "collect_data_status": collect_data_status,
        "minutes_offset": LOADER_MINUTES_OFFSET
    }

@app.post("/collect_data/deactivate")
def toogle_collect_data():
    collect_data_status = False
    return {
        "collect_data_status": collect_data_status,
        "minutes_offset": LOADER_MINUTES_OFFSET
    }

#periodically get the data
@scheduler.scheduled_job("interval", minutes= LOADER_MINUTES_OFFSET)
def collect_data() :
    if not collect_data_status:
        print("Data collection is disabled")
        return
    execute_data_collection()

def start_scheduler():
    scheduler.start()

if __name__ == "__main__":
    threading.Thread(target=start_scheduler).start()
    uvicorn.run(app, host=loader_fast_api_host, port= loader_fast_api_port)