# Match trainer/MLflow; their pinned dependencies need a supported Python version.
FROM python:3.11-slim
WORKDIR /app

COPY predict/requirements-predictor.txt .

RUN pip install --no-cache-dir -r requirements-predictor.txt

COPY predict/ ./predict
COPY repository/ ./repository/
COPY utils/ ./utils/

#EXPOSE 8501

CMD ["python", "-u", "-m", "predict.main"]
