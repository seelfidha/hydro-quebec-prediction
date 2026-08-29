CREATE TABLE processed_ids (
    id BIGINT PRIMARY KEY,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pannes (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nb_clients_impactes VARCHAR(255),
    date_debut TIMESTAMP NULL,
    date_fin TIMESTAMP NULL,
    pannep TEXT,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    statut VARCHAR(255),
    info_non_utilise VARCHAR(255),
    cause VARCHAR(255),
    id_municipalite VARCHAR(255),
    id_msg_panne TEXT,
    callID_processed BIGINT,
    CONSTRAINT fk_callID_processed FOREIGN KEY (callID_processed) REFERENCES processed_ids(id)
);