from threading import Lock

import mlflow
import pandas as pd
import h2o
import uvicorn
from fastapi import FastAPI, BackgroundTasks
from minio import Minio

from h2o.automl import H2OAutoML
from mlflow import MlflowClient
from psycopg.types import none

from repository.pannes_repository import get_pannes
from train.utils_trainer import convert_rows_to_h2o_format, handle_h2o_categorical_data, save_minio_instance
from utils.params_config import ml_flow_url, h2o_port, h2o_host, minio_url, minio_access_key, minio_secret, \
    trainer_fast_api_host, trainer_fast_api_port

bucket = "csv-data"
experiment_name = "hydro-quebec-predictions"


def init_mlflow_experiment(client):
    experiment = client.get_experiment_by_name(experiment_name)
    if experiment is None:
        print("mlflow new experiment")
        experiment_id = client.create_experiment(experiment_name)
        print("mlflow new experiment created")
    else:
        print("mlflow experiment already exists")
        experiment_id = experiment.experiment_id
        if experiment.lifecycle_stage == "deleted":
            print("mlflow experiment must be restored")
            client.restore_experiment(experiment_id)

    mlflow.set_experiment(experiment_id=experiment_id)
    print("mlflow experiment name : ", experiment.name)
    return client.get_experiment(experiment_id)

def init_minio():
    client_minio =Minio(
        minio_url,
        access_key=minio_access_key,
        secret_key=minio_secret,
        secure=False
    )
    if not client_minio.bucket_exists(bucket):
        client_minio.make_bucket(bucket)
    return client_minio

app = FastAPI()

mlflow.set_tracking_uri(ml_flow_url)
mlflow_client = MlflowClient(tracking_uri=ml_flow_url)
mlflow_experiment = init_mlflow_experiment(mlflow_client)
training_lock = Lock()
client_minio = init_minio()

@app.get("/train_data/health")
def train_data_status():
    return {
        "train_data_status": 'ok',
    }

@app.get("/train_data/status/{run_id}")
def train_data_status(run_id):
    run = mlflow_client.get_run(run_id)
    return {
        "id": run.info.run_id,
        "status": run.info.status
    }

@app.post("/train_data/start")
def launch_training(background_tasks: BackgroundTasks):
    print("new run launched")
    run = mlflow_client.create_run(mlflow_experiment.experiment_id)
    run_id = run.info.run_id
    print("run id: ", run_id)
    background_tasks.add_task(train_model, run_id)
    return {"run_id": run_id}

def train_model(run_id):
    with training_lock:
        with mlflow.start_run(run_id=run_id):
            print("Get the data")
            train_frame = get_data(client_minio)
            target = "nb_clients_impactes"
            predictors = [column for column in train_frame.columns if column != target]
            train, valid, test = train_frame.split_frame(ratios=[0.7, 0.15], seed=42)

            aml = H2OAutoML(
                max_models=2,
                seed=42,
                sort_metric="RMSE",
                project_name="hydroquebec-predictions"
            )

            aml.train(x=predictors, y=target, training_frame=train, validation_frame=valid)

            if aml.leader is none:
                raise RuntimeError("No leaderboard found")

            leader = aml.leader
            performance = leader.model_performance(test)

            mlflow.log_param("target", target)
            mlflow.log_param("predictors", ",".join(predictors))
            mlflow.log_param("train_rows", train.nrows)
            mlflow.log_param("valid_rows", valid.nrows)
            mlflow.log_param("test_rows", test.nrows)
            mlflow.log_metric("rmse", performance.rmse())
            mlflow.log_metric("mae", performance.mae())

            print("Leaderboard:")
            print(aml.leaderboard.head(rows=10))
            print(f"Leader model: {leader.model_id}")
            print(f"Test RMSE: {performance.rmse()}")
            print(f"Test MAE: {performance.mae()}")


def get_data(minio):
    print("read database")
    rows = get_pannes()
    print(f"convert {len(rows)} rows to h2o format")
    feature_rows = convert_rows_to_h2o_format(rows)
    print("create pandas frame")
    pandas_frame = pd.DataFrame(feature_rows)
    print("save version data to minio")
    save_minio_instance(pandas_frame, minio, bucket)
    return handle_h2o_categorical_data(pandas_frame)


def init_h2o():
    h2o.init(
        ip=h2o_host,
        port=h2o_port,
        start_h2o=True,
        verbose=True
    )

if __name__ == "__main__":
    print("initiate h2o")
    init_h2o()
    uvicorn.run(app, host=trainer_fast_api_host, port= trainer_fast_api_port)
