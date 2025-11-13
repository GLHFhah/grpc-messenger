FROM python:3.12-slim

WORKDIR /grpc-messenger

COPY client/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY client/client.py messenger/client/
COPY proto messenger/proto

ENTRYPOINT ["python", "-m", "messenger.client.client"]