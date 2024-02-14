import asyncio
from telethon import TelegramClient
from config import api_id, api_hash, my_chat_id, bot_token, SHUTTLE_KEY
from telegram_grebber import telegram_grabber
from collections import deque
import asyncio
from shuttleai import *
import asyncio

prompt = """На русском языке:ё
    1) Опишите заголовок события, обращая внимание на ключевые аспекты и исключая дополнительные детали.
    2) Укажите место события в формате: Город (при наличии), улица (при наличии), дом (при наличии). Уточните, что все события происходят в Нижегородской области.
    3) Переформулируйте информацию, предоставив более точный контекст и избегая лишних эмоциональных вставок.
    """

tg_channels = [-1001941183965]
session = "myGrab"
amount_messages = 10
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
bot = TelegramClient("bot_session", api_id, api_hash, loop=loop)
bot.start(bot_token=bot_token)
posted_q = deque(maxlen=amount_messages)


async def gpt_response(input_text):
    async with ShuttleAsyncClient(SHUTTLE_KEY, timeout=60) as shuttle:
        #shuttle.base_url = "https://api.shuttleai.app"
        response = await shuttle.chat_completion(
             model="gpt-3.5-turbo",
             messages=[{"role":"user","content":input_text + prompt}],
             stream=False,
             plain=False,
             internet=False,
             max_tokens=100,
             temperature=0.5,
        )
        return response

def filter_func(text):
    words = text.lower().split()
    key_words = [
        "реклам",
        "розыгрыш",
        "друз",
        "рекоменд",
        "показ",
        "бесплат",
    ]
    for word in words:
        for key in key_words:
            if key in word:
                return False
    return True


async def send_message_func(post, photo_path):
    if photo_path == "":
        await bot.send_message(my_chat_id, post)
    else:
        await bot.send_file(entity=my_chat_id, file=photo_path, caption=post)


main_client = telegram_grabber(session=session, api_id=api_id, api_hash=api_hash, telegram_channels=tg_channels,
                               send_message_func=send_message_func, check_ban_words=filter_func,
                               parsing_func=gpt_response, loop=loop)

try:
    main_client.run_until_disconnected()
finally:
    loop.close()
