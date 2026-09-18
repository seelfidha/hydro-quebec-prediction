from datetime import datetime
from io import BytesIO

import h2o

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

def handle_h2o_categorical_data(pandas_frame):
    train_frame = h2o.H2OFrame(pandas_frame)
    print(train_frame.col_names)
    for category in CATEGORICAL_COLUMNS:
        train_frame[category] = train_frame[category].asfactor()
    return train_frame

def convert_rows_to_h2o_format(rows):
    # adapt the data to h2o format
    converted_rows = []
    for data in rows:

        dict = convert_db_row_to_dict(data)

        new_feature = convert_dict_to_json(dict)

        if new_feature['nb_clients_impactes'] is not None:
            converted_rows.append(new_feature)

    if(len(converted_rows) < 20):
        raise RuntimeError(
            "less than 20 rows are available for learning"
        )
    return converted_rows

def convert_db_row_to_dict(row):
    # convert data from database to key value
    result = {}
    for i in range(0, len(PANNES_COLUMNS)) :
        key = PANNES_COLUMNS[i]
        result[key] = row[i]
    return result

def convert_dict_to_json(row):
    date_debut = row["date_debut"]
    date_fin = row["date_fin"]
    if isinstance(date_debut, str):
        date_debut = datetime.fromisoformat(date_debut)
    if isinstance(date_fin, str):
        date_fin = datetime.fromisoformat(date_fin) if date_fin else None
    return  {
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

def to_float(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def save_minio_instance(pandas_frame, minio, bucket):
    csv_bytes = pandas_frame.to_csv(index=False).encode("utf-8")
    csv_buffer = BytesIO(csv_bytes)
    minio.put_object(
        bucket_name= bucket,
        object_name="datasets/train.csv",
        data=csv_buffer,
        length=len(csv_bytes),
        content_type="text/csv"
    )
