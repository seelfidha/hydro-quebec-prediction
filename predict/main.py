from typing import Any

import mlflow
import uvicorn
from fastapi import Body, FastAPI

from predict.utils_predictor import get_model_champion
from utils.params_config import ml_flow_url, predictor_fast_api_host, predictor_fast_api_port

mlflow.set_tracking_uri(ml_flow_url)
app = FastAPI()

model_champion = get_model_champion()


@app.post("/predict")
def predict(payload: dict[str, Any] = Body(...)):
    print(payload)
    return {"received": payload}

if __name__ == "__main__":
    uvicorn.run(app, host=predictor_fast_api_host, port= predictor_fast_api_port)
