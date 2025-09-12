FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Config Postgres (DB éphémère)
RUN service postgresql start && \
    su - postgres -c "psql -c \"CREATE DATABASE obesitrack_db;\"" && \
    su - postgres -c "psql -c \"CREATE USER postgres WITH PASSWORD '';\"" && \
    su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE obesitrack_db TO postgres;\""

ENV HF_HOME=/app/hf_home

RUN mkdir -p /app/hf_home && chmod -R 777 /app/hf_home

CMD service postgresql start && uvicorn main:app --host 0.0.0.0 --port 7860

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
