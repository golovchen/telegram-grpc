import asyncio
import os
import traceback

import grpc
import telethon
from telethon import TelegramClient, functions, events, types
from telethon.tl.types import PeerUser, PeerChat, PeerChannel

import protos_pb2_grpc
from protos_pb2 import User, GetUserRequest, NewMessageEvent, Message, Channel, Chat, Photo, ForwardResponse, \
    ForwardRequest, SendMessageRequest, SendMessageResponse, SearchRequest, SearchResponse, FoundedChat, \
    GetHistoryResponse, GetHistoryRequest, GetMessagesRequest, GetMessagesResponse, CreateChatResponse, \
    CreateChatRequest, FullUser, Forward

api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
client = TelegramClient("session", api_id, api_hash)
client.start()

messages = []

@client.on(events.NewMessage())
async def handle_new_message(event):
    if isinstance(event.message, types.Message):
        print("got " + str(event.message))
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
            chat_user=telethon_user_to_proto(chat),
            chat_channel=telethon_channel_to_proto(chat),
            chat_chat=telethon_chat_to_proto(chat)
        )

        message_event = NewMessageEvent(message=proto_message)
        messages.append(message_event)
        print("add " + str(message_event))


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

def telethon_forward_to_proto(forward: telethon.tl.custom.forward.Forward):
    if isinstance(forward, telethon.tl.custom.forward.Forward):
        return Forward(chat_id=forward.chat_id)
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
    async def GetUser(self, request: GetUserRequest, context: grpc.aio.ServicerContext) -> FullUser:
        try:
            print("get user " + str(request))
            if request.HasField('username'):
                result = await client(functions.users.GetFullUserRequest(request.username))
            elif request.HasField('user_id'):
                result = await client(functions.users.GetFullUserRequest(
                    id=request.user_id
                ))
            print(result)
            result = result.users[0]
            return FullUser(id=result.id, first_name=result.first_name, last_name=result.last_name, username=result.username)
        except:
            traceback.print_exc()

    async def GetNewMessages(self, request, context) -> NewMessageEvent:
        try:
            print("get new messages")
            while True:
                while not messages:
                    await asyncio.sleep(0.1)

                yield messages.pop(0)
        except:
            traceback.print_exc()

    async def Forward(self, request:ForwardRequest, context) -> ForwardResponse:
        print("forward " + str(request))
        from_peer = None
        if request.HasField('from_user_id'):
            from_peer=PeerUser(user_id=request.from_user_id)
        elif request.HasField('from_chat_id'):
            from_peer=PeerChat(chat_id=request.from_chat_id)
        elif request.HasField('from_channel_id'):
            from_peer=PeerChannel(channel_id=request.from_channel_id)

        to_peer = None
        if request.HasField('to_user_id'):
            to_peer=PeerUser(user_id=request.to_user_id)
        elif request.HasField('to_chat_id'):
            to_peer=PeerChat(chat_id=request.to_chat_id)
        elif request.HasField('to_channel_id'):
            to_peer=PeerChannel(channel_id=request.to_channel_id)

        await client.forward_messages(entity=to_peer, messages=request.message_id, from_peer=from_peer)
        return ForwardResponse()

    async def SendMessage(self, request: SendMessageRequest, context) -> SendMessageResponse:
        entity = None
        if request.HasField('to_username'):
            entity = request.to_username
        elif request.HasField('to_user_id'):
            entity=PeerUser(user_id=request.to_user_id)
        elif request.HasField('to_chat_id'):
            entity=PeerChat(chat_id=request.to_chat_id)

        await client.send_message(entity, request.text)
        return SendMessageResponse()

    async def Search(self, request: SearchRequest, context) -> SearchResponse:
        if request.HasField('limit'):
            limit = request.limit
        else:
            limit = 100
        result = await client(functions.contacts.SearchRequest(
            q=request.query,
            limit=limit
        ))
        if result.chats:
            chats = [FoundedChat(id=c.id, title=c.title, participants_count=c.participants_count) for c in result.chats]
        else:
            chats = []
        return SearchResponse(chats=chats)

    async def CreateChat(self, request: CreateChatRequest, context) -> CreateChatResponse:
        result = await client(functions.messages.CreateChatRequest(
            users=list(request.user_ids),
            title=request.title
        ))
        return CreateChatResponse(chat=telethon_chat_to_proto(result.chats[0]))

    async def GetHistory(self, request: GetHistoryRequest, context) -> GetHistoryResponse:
        result = await client(telethon.tl.functions.messages.GetHistoryRequest(
            peer=request.username,
            offset_id=request.offset_id,
            offset_date=request.offset_date,
            add_offset=request.add_offset,
            limit=request.limit,
            max_id=request.max_id,
            min_id=request.min_id,
            hash=request.hash
        ))

        return GetHistoryResponse(messages=[Message(
            id=m.id,
            text=m.text,
            raw_text=m.raw_text,
            photo=telethon_photo_to_proto(m.photo),
            sender_user = telethon_user_to_proto(m.sender),
            sender_channel=telethon_channel_to_proto(m.sender),
            chat_user=telethon_user_to_proto(m.chat),
            chat_channel=telethon_channel_to_proto(m.chat),
            chat_chat=telethon_chat_to_proto(m.chat)
        ) for m in result.messages])

    async def GetMessages(self, request: GetMessagesRequest, context) -> GetMessagesResponse:
        entity = None
        if request.HasField('username'):
            entity = request.username
        elif request.HasField('user_id'):
            entity = PeerUser(user_id=request.user_id)

        result = await client.get_messages(
            entity=entity,
            offset_id=request.offset_id,
            add_offset=request.add_offset,
            limit=request.limit if request.limit > 0 else None
        )
        return GetMessagesResponse(messages=[Message(
            id=m.id,
            text=m.text,
            raw_text=m.raw_text,
            photo=telethon_photo_to_proto(m.photo),
            sender_user = telethon_user_to_proto(m.sender),
            sender_channel=telethon_channel_to_proto(m.sender),
            chat_user=telethon_user_to_proto(m.chat),
            chat_channel=telethon_channel_to_proto(m.chat),
            chat_chat=telethon_chat_to_proto(m.chat),
            forward=telethon_forward_to_proto(m.forward)
        ) for m in result])

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