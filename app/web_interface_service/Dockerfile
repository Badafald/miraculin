FROM python:3.10-slim

RUN useradd -m web-iface-user

WORKDIR /app
COPY requirements.txt /app/


RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/


RUN chown -R web-iface-user:web-iface-user /app

USER web-iface-user
EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "web_interface_service:app"]
