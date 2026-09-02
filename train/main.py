from datetime import datetime
from random import seed

import h2o
import mlflow
from h2o.automl import H2OAutoML
from repository.pannes_repository import get_pannes

PANNES_COLUMNS = [
    "id",
    "nb_clients_impactes",
    "date_debut",
    "date_fin",
    "pannep",
    "longitude",
    "latitude",
    "statut",
    "info_non_utilise",
    "cause",
    "id_municipalite",
    "id_msg_panne",
    "callid_processed",
]

CATEGORICAL_COLUMNS = [
    "pannep",
    "statut",
    "id_municipalite",
    "is_active",
    "debut_day_of_week",
]

def convert_row(row):
    # convert data from database to key value
    result = {}
    for i, key in PANNES_COLUMNS:
        result[i] = row[key]
    return result

def to_float(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def convert_all_rows(rows):
    # adapt the data to h2o format
    converted_rows = []
    for data in rows:

        row = convert_row(data)

        date_debut = row["date_debut"]
        date_fin = row["date_fin"]

        new_feature = {
            "nb_clients_impactes": to_float(row["nb_clients_impactes"]),
            "longitude": to_float(row["longitude"]),
            "latitude": to_float(row["latitude"]),
            "cause": row["cause"] or "unknown",
            "statut": row["statut"] or "unknown",
            "id_municipalite": row["id_municipalite"] or "unknown",
            "pannep": row["pannep"] or "unknown",
            "debut_hour": date_debut.hour,
            "debut_day_of_week": date_debut.weekday(),
            "debut_month": date_debut.month,
            "is_active": "yes" if date_fin is None else "no",
            "duration_minutes": (
                (date_fin - date_debut).total_seconds() / 60
                if isinstance(date_fin, datetime)
                else None
            ),
        }
        if new_feature['nb_clients_impactes'] is not None:
            converted_rows.append(new_feature)

    if(len(converted_rows) < 20):
        raise RuntimeError(
            "less than 20 rows are available for learning"
        )
    return converted_rows

def construct_train_frame(feature_rows):
    train_frame = h2o.H2OFrame(feature_rows)
    for category in CATEGORICAL_COLUMNS:
        train_frame[category] = train_frame[category].asfactor()
    return train_frame

def init_mlflow_h2o():
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("hydro-quebec-predictions")
    h2o.init()

if __name__ == '__main__':

    rows = get_pannes()
    feature_row = convert_all_rows(rows)
    init_mlflow_h2o()
    with mlflow.start_run(run_name="h2o_automl_nb_clients_impactes"):
        train_frame = construct_train_frame(rows)
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
