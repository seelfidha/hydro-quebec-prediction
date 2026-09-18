from contextlib import asynccontextmanager
from typing import Any

import h2o
import mlflow
import pandas as pd
import uvicorn
from fastapi import Body, FastAPI

from predict.utils_predictor import get_model_champion
from utils.data_preprocessor import handle_h2o_categorical_data
from utils.params_config import ml_flow_url, predictor_fast_api_host, predictor_fast_api_port, h2o_host, h2o_port


mlflow.set_tracking_uri(ml_flow_url)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when FastAPI starts
    h2o.init(
        ip=h2o_host,
        port=h2o_port,
        start_h2o=True,
        verbose=True
    )
    yield
app = FastAPI(lifespan=lifespan)

@app.get("/predict_data/health")
def train_data_status():
    return {
        "predict_data_status": 'ok',
    }


@app.post("/predict")
def predict(payload: dict[str, Any] = Body(...)):

    print(payload)

    # champion_info = get_model_champion_info()
    # print(f'Model champion name: {champion_info.name}')
    # print(f'Model champion version: {champion_info.version}')

    pandas_frame = pd.DataFrame([payload])

    # pandas_frame = handle_h2o_categorical_data(pandas_frame)

    prediction = get_model_champion().predict(pandas_frame)

    print(f'prediction:{prediction}')

    return {"prediction": prediction}

if __name__ == "__main__":
    uvicorn.run(app, host=predictor_fast_api_host, port= predictor_fast_api_port)
