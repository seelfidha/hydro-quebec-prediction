FROM python:3.11-slim
WORKDIR /app
# H2O needs a Java runtime
RUN apt-get update \
    && apt-get install -y --no-install-recommends default-jre-headless \
    && rm -rf /var/lib/apt/lists/*
COPY train/requirements-trainer.txt .
RUN pip install --no-cache-dir -r requirements-trainer.txt

COPY train/ /app/train
COPY repository/ /app/repository/
COPY utils/ /app/utils/

#EXPOSE 8000

CMD ["python", "-u", "-m", "train.main"]
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
