import asyncio
import os
import traceback

import grpc
from telethon import TelegramClient, functions, events, types
from telethon.tl.types import PeerUser

import protos_pb2_grpc
from protos_pb2 import User, GetUserRequest, NewMessageEvent, Message, Channel, Chat, Photo

api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
client = TelegramClient("session", api_id, api_hash)
client.start()

messages = []

@client.on(events.NewMessage())
async def handle_new_message(event):
    if isinstance(event.message, types.Message):
        sender = await event.message.get_sender()
        chat = await event.message.get_chat()
        message = event.message
        proto_message = Message(
            id=message.id,
            text=message.text,
            raw_text=message.raw_text,
            photo=telethon_photo_to_proto(message.photo),
            sender_user = telethon_user_to_proto(sender),
            sender_channel=telethon_channel_to_proto(sender),
            chat_user=telethon_user_to_proto(sender),
            chat_channel=telethon_channel_to_proto(chat),
            chat_chat=telethon_chat_to_proto(chat)
        )

        message_event = NewMessageEvent(message=proto_message)
        messages.append(message_event)
        print(message_event)


def telethon_photo_to_proto(photo):
    if photo:
        return Photo(id=photo.id)
    else:
        return None


def telethon_chat_to_proto(chat):
    if isinstance(chat, types.Chat):
        return Chat(id=chat.id, title=chat.title, participants_count=chat.participants_count)
    else:
        return None


def telethon_channel_to_proto(sender):
    if isinstance(sender, types.Channel):
        return Channel(id=sender.id, title=sender.title)
    else:
        return None


def telethon_user_to_proto(telethon_user):
    if isinstance(telethon_user, types.User):
        return User(id=telethon_user.id, bot=telethon_user.bot, is_self=telethon_user.is_self,
                    first_name=telethon_user.first_name,
                    last_name=telethon_user.last_name, username=telethon_user.username)
    else:
        return None


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
            traceback.print_exc()

    async def GetNewMessages(self, request, context) -> NewMessageEvent:
        try:
            print("get new messages")
            while True:
                while not messages:
                    await asyncio.sleep(0.1)

                yield messages.pop()
        except:
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