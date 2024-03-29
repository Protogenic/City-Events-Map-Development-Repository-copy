from telethon import TelegramClient
from config.config import api_id, api_hash, bot_token
from config.sources.sources import tg_channels
from serivces.telegram_grebber import telegram_grabber
import asyncio
session = "myGrab"
amount_messages = 10
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
bot = TelegramClient("bot_session", api_id, api_hash, loop=loop)
bot.start(bot_token=bot_token)

main_client = telegram_grabber(session=session, api_id=api_id, api_hash=api_hash, loop=loop,tg_channels = tg_channels)

try:
    main_client.run_until_disconnected()
finally:
    loop.close()
