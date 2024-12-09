FROM python:3.10-slim

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5002

CMD ["gunicorn", "-b", "0.0.0.0:5002", "storage_service:app"]
