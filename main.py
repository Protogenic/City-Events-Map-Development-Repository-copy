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

prompt = """На русском языке:
    1) Опишите заголовок события, обращая внимание на ключевые аспекты и исключая дополнительные детали.
    2) Укажите место события в формате: Город (при наличии), улица (при наличии), дом (при наличии). Уточните, что все события происходят в Нижегородской области.
    3) Переформулируйте информацию, предоставив более точный контекст и избегая лишних эмоциональных вставок.
    """

async def parsing_func(input_text):
    response = await g4f.ChatCompletion.create_async(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": input_text + prompt}],
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


async def send_message_func(text):
    await bot.send_message(entity=my_chat_id, parse_mode="html", link_preview=False, message=text)


telegram_channels = [-1001941183965]


def check_ban_words(text):
    words = text.lower().split()
    key_words = [
        "реклам",
        "розыгрыш",

    ]

    for word in words:
        for key in key_words:
            if key in word:
                return False

    return True


client = telegram_parser(session, api_id, api_hash, telegram_channels, check_ban_words=check_ban_words,
                         parse_func=parsing_func, loop=loop, send_message_func=send_message_func)

try:
    client.run_until_disconnected()
except Exception as e:
    message = f'&#9888; ERROR: telegram parser (all parsers) is down! \n{e}'
finally:
    loop.close()
