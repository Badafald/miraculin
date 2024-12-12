FROM python:3.10-slim

RUN useradd -m storage-service-user

WORKDIR /app
COPY requirements.txt /app/


RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/


RUN chown -R storage-service-user:storage-service-user /app

USER storage-service-user
EXPOSE 5002

CMD ["gunicorn", "-b", "0.0.0.0:5002", "storage_service:app"]
