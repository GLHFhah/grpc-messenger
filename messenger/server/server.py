import grpc
import os
from messenger.proto import messenger_pb2
from messenger.proto import messenger_pb2_grpc
from threading import Lock
from google.protobuf.timestamp_pb2 import Timestamp
from concurrent import futures
from queue import SimpleQueue, Empty
import time

class MessengerService(messenger_pb2_grpc.MessengerServerServicer):
    def __init__(self):
        self._lock = Lock()
        self._clients = []

    def SendMessage(self, request, context):
        send_time = Timestamp()
        send_time.GetCurrentTime()

        message = messenger_pb2.Message(
            author=request.author,
            text=request.text,
            sendTime=send_time
        )
        
        with self._lock:
            for client in self._clients:
                client.put(message)
        
        return messenger_pb2.MessageResponse(sendTime=send_time)

    def ReadMessages(self, request, context):
        buffer = SimpleQueue()
        
        with self._lock:
            self._clients.append(buffer)
        
        while True:
            try:
                message = buffer.get(timeout=3.0)
                yield message
            except Empty:
                if not context.is_active():
                    break
        with self._lock:
            if buffer in self._clients:
                self._clients.remove(buffer)


def serve():
    port = os.environ.get('MESSENGER_SERVER_PORT', '51075')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    messenger_pb2_grpc.add_MessengerServerServicer_to_server(MessengerService(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    import os
    serve()