FROM python:3.12-slim

WORKDIR /grpc-messenger

COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/server.py messenger/server/
COPY proto messenger/proto

ENTRYPOINT ["python", "-m", "messenger.server.server"]