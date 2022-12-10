from telethon import TelegramClient
import os

api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
client = TelegramClient("session", api_id, api_hash)
client.start()
client.run_until_disconnected()