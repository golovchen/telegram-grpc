from concurrent import futures

import grpc
from telethon import TelegramClient
import os

import protos_pb2_grpc


class TelegramServer(protos_pb2_grpc.TelegramClient):
    pass


api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
client = TelegramClient("session", api_id, api_hash)
client.start()

client.run_until_disconnected()

port = '50051'
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
protos_pb2_grpc.add_TelegramClientServicer_to_server(TelegramServer(), server)
server.add_insecure_port('[::]:' + port)
server.start()
print("Server started, listening on port " + port)
server.wait_for_termination()