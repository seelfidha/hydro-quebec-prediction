import mlflow
import pandas as pd
import h2o

from h2o.automl import H2OAutoML
from minio import Minio

from repository.pannes_repository import get_pannes
from train.utils import convert_rows_to_h2o_format, handle_h2o_categorical_data, save_minio_instance
from utils.params_config import ml_flow_url, h2o_port, h2o_host, minio_url, minio_access_key, minio_secret

bucket = "csv-data"
experiment_name = "hydro-quebec-predictions"

def init_mlflow():
    mlflow.set_tracking_uri(ml_flow_url)
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        experiement_id = mlflow.create_experiment(experiment_name)
        experiment = mlflow.get_experiment(experiement_id)
    mlflow.set_experiment(experiment.name)

def init_h2o():
    h2o.init(
        ip=h2o_host,
        port=h2o_port,
        start_h2o=True,
        verbose=True
    )

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


if __name__ == '__main__':
    print("initiate mlflow & h2o")
    init_mlflow()
    print("initiate h2o")
    init_h2o()
    print("initiate minio")
    client_minio = init_minio()
    with mlflow.start_run(run_name="h2o_automl_nb_clients_impactes"):
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
