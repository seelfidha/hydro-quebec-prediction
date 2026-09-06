FROM python
WORKDIR /app
COPY load/requirements-loader.txt .
RUN pip install --no-cache-dir -r requirements-loader.txt
COPY load/ ./load
COPY repository/ ./repository/
COPY utils/ ./utils/

#EXPOSE 8501

CMD ["python", "-u", "-m", "load.main"]
