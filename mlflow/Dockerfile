FROM python:3.11-slim

WORKDIR /mlflow

RUN pip install --no-cache-dir mlflow==2.16.2

EXPOSE 5000

CMD ["mlflow", "server", \
     "--backend-store-uri", "sqlite:///database/mlflow.db", \
     "--default-artifact-root", "/mlflow/mlruns", \
     "--host", "0.0.0.0", "--port", "5000"]