# Match trainer/MLflow; their pinned dependencies need a supported Python version.
FROM python:3.11-slim
WORKDIR /app

# Loading an MLflow H2O model starts a local H2O JVM.
RUN apt-get update \
    && apt-get install -y --no-install-recommends default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

COPY predict/requirements-predictor.txt .

RUN pip install --no-cache-dir -r requirements-predictor.txt

COPY predict/ ./predict
COPY repository/ ./repository/
COPY utils/ ./utils/

#EXPOSE 8501

CMD ["python", "-u", "-m", "predict.main"]
