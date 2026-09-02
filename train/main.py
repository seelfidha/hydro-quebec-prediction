from datetime import datetime
import pandas as pd
import h2o
import mlflow
from h2o.automl import H2OAutoML
from repository.pannes_repository import get_pannes
from train.utils import convert_rows_to_h2o_format, construct_h2o_format_frame


def init_mlflow_h2o():
    mlflow.set_tracking_uri("http://mlflow:5000")
    experiment_name = "hydro-quebec-predictions"
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        experiement_id = mlflow.create_experiment(experiment_name)
        experiment = mlflow.get_experiment(experiement_id)
    mlflow.set_experiment(experiment.name)
    print("initiate h2o")
    h2o.init(
        ip="127.0.0.1",
        port=54321,
        start_h2o=True,
        verbose=True
    )

if __name__ == '__main__':
    print("read database data")
    rows = get_pannes()
    print("convert data to h2o format")
    feature_row = convert_rows_to_h2o_format(rows)
    print("convert data to h2o format")
    print("initiate mlflow & h2o")
    init_mlflow_h2o()
    print("convert data to h2o format")
    with mlflow.start_run(run_name="h2o_automl_nb_clients_impactes"):
        train_frame = construct_h2o_format_frame(feature_row)
        target = "nb_clients_impactes"
        predictors = [column for column in train_frame.columns if column != target]
        train, valid, test = train_frame.split_frame(ratios=[0.7, 0.15], seed=42)

        aml = H2OAutoML(
            max_models=2,
            seed = 42,
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
