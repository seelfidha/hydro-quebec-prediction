import threading
import uvicorn

from fastapi import FastAPI, Response
from load.utils_loader import execute_data_collection
from apscheduler.schedulers.blocking import BlockingScheduler

from repository.processed_id_repository import delete_processed_id, is_processed
from utils.params_config import loader_fast_api_port, loader_fast_api_host, LOADER_MINUTES_OFFSET
app = FastAPI()
scheduler = BlockingScheduler()
collect_data_status = True

@app.get("/collect_data/status")
def get_collect_data_status():
    return {
        "collect_data_status": collect_data_status,
        "minutes_offset": LOADER_MINUTES_OFFSET
    }

@app.post("/collect_data/activate")
def toogle_collect_data():
    global collect_data_status
    collect_data_status = True
    print("Data loader activated")
    return {
        "collect_data_status": collect_data_status,
        "minutes_offset": LOADER_MINUTES_OFFSET
    }

@app.post("/collect_data/deactivate")
def toogle_collect_data():
    global collect_data_status
    collect_data_status = False
    print("Data loader deactivated")
    return {
        "collect_data_status": collect_data_status,
        "minutes_offset": LOADER_MINUTES_OFFSET
    }

@app.delete("/collect_data/delete/{item_id}")
def clean_id(item_id):
    if is_processed(item_id):
        print("Item id found, starting cleaning")
        result = delete_processed_id(item_id)
        if result:
            print("deleted processed id")
            return Response(status_code=200)
        else:
            print("error deleting processed id")
            return Response(status_code=500)
    else:
        print("Nothing to delete")
        return Response(status_code=200)

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
