FROM python
WORKDIR /app
COPY load/requirements-loader.txt .
RUN pip install --no-cache-dir -r requirements-loader.txt
COPY load/ /app/load
COPY repository/ /app/repository/

#EXPOSE 8501

CMD ["python", "-u", "-m", "load.main"]
