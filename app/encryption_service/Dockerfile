FROM python:3.10-slim

RUN useradd -m enrypt-user

WORKDIR /app
COPY requirements.txt /app/


RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/


RUN chown -R enrypt-user:enrypt-user /app

USER enrypt-user

EXPOSE 5001
CMD ["gunicorn", "-b", "0.0.0.0:5001", "encryption_service:app"]
