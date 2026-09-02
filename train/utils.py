from datetime import datetime
import pandas as pd
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


def construct_h2o_format_frame(feature_rows):
    pandas_frame = pd.DataFrame(feature_rows)
    train_frame = h2o.H2OFrame(pandas_frame)
    print(train_frame.col_names)
    for category in CATEGORICAL_COLUMNS:
        train_frame[category] = train_frame[category].asfactor()
    return train_frame

def convert_rows_to_h2o_format(rows):
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


def to_float(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def convert_row(row):
    # convert data from database to key value
    result = {}
    for i in range(0, len(PANNES_COLUMNS)) :
        key = PANNES_COLUMNS[i]
        result[key] = row[i]
    return result