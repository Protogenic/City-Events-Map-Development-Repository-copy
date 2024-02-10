import asyncio
from telethon import TelegramClient
from config import api_id, api_hash, my_chat_id, bot_token
from tg_parser import telegram_parser

import g4f

from g4f.Provider import (
    Bard,
    Bing,
    HuggingChat,
    OpenAssistant,
    OpenaiChat,
)

# Usage:

promt = """На русском языке:
       "1) Опишите заголовок события, уделяя внимание ключевым аспектам.
        2)  Укажите место события в формате Город, улица (при наличии), дом (при наличии), и исключите лишние локационные детали.(Все события происходят В Нижнем Новгороде)
        3) Переформулируйте информацию, предоставив более точный контекст."""


async def parsing_func(input_text):
    response = await g4f.ChatCompletion.create_async(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": promt + input_text}],
        # stream=True,
    )
    output_text = ""
    for msg in response:
        output_text += msg
    return output_text


session = 'myGrab'
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
bot = TelegramClient('bot', api_id, api_hash, loop=loop)
bot.start(bot_token=bot_token)

telegram_channels = [-1001941183965]


def check_ban_words(text):
    words = text.lower().split()

    key_words = [

    ]

    for word in words:
        if 'газ' in word and len(word) < 6:  # газ, газу, газом, газа
            return True

        for key in key_words:
            if key in word:
                return True

    return False


async def send_message_func(text):
    await bot.send_message(entity=my_chat_id, message=text)


client = telegram_parser(session, api_id, api_hash, telegram_channels, parse_func=parsing_func, loop=loop)

try:
    client.run_until_disconnected()
except Exception as e:
    message = f'&#9888; ERROR: telegram parser (all parsers) is down! \n{e}'
finally:
    loop.close()
