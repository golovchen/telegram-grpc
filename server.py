import traceback

import grpc
from telethon import TelegramClient, functions
import os
import asyncio

import protos_pb2_grpc
from protos_pb2 import User, GetUserRequest

api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
client = TelegramClient("session", api_id, api_hash)
client.start()

class TelegramServer(protos_pb2_grpc.TelegramClientServicer):
    async def GetUser(self, request: GetUserRequest, context: grpc.aio.ServicerContext) -> User:
        try:
            print("get user " + str(request))
            result = await client(functions.users.GetFullUserRequest(
                id=request.user_id
            ))
            print(result)
            result = result.users[0]
            return User(first_name=result.first_name, last_name=result.last_name, username=result.username)
        except:
            print("exception")
            traceback.print_exc()



async def serve() -> None:
    try:
        server = grpc.aio.server()
        protos_pb2_grpc.add_TelegramClientServicer_to_server(TelegramServer(), server)
        listen_addr = '[::]:50051'
        server.add_insecure_port(listen_addr)
        print("Starting server on %s", listen_addr)
        await server.start()
        await server.wait_for_termination()
    except:
        traceback.print_exc()

loop = asyncio.get_event_loop()
loop.run_until_complete(serve())