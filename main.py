import asyncio

from telethon import TelegramClient, events
from transformers import AutoTokenizer, T5ForConditionalGeneration
from config import api_id, api_hash, my_chat_id, bot_token
from pullenti_wrapper.langs import (
    set_langs,
    RU
)

set_langs([RU])
from pullenti_wrapper.processor import (
    Processor,
    GEO,
    ADDRESS
)
from tg_parser import telegram_parser

model_name = "IlyaGusev/rut5_base_headline_gen_telegram"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)
processor = Processor([GEO, ADDRESS])
from pullenti_wrapper.referent import Referent


def parse_func(input_text):
    input_ids = tokenizer(
        [input_text],
        max_length=600,
        add_special_tokens=True,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    )["input_ids"]

    output_ids = model.generate(
        input_ids=input_ids
    )[0]
    headline = tokenizer.decode(output_ids, skip_special_tokens=True)
    output_text = "Title: " + headline + "\n\n" + "Place: "

    def display_shortcuts(referent, level=0):
        tmp = {}
        a = ""
        b = ""
        for key in referent.__shortcuts__:
            value = getattr(referent, key)
            if value in (None, 0, -1):
                continue
            if isinstance(value, Referent):
                display_shortcuts(value, level + 1)
            else:
                if key == 'type':
                    a = value
                if key == 'name':
                    b = value
                    # print('ok', value)
                if key == 'house':
                    a = "дом"
                    b = value
                    tmp[a] = b
                if key == 'flat':
                    a = "квартира"
                    b = value
                    # print('ok', value)
                    tmp[a] = b
            if key == 'corpus':
                a = "корпус"
                b = value
                tmp[a] = b
        tmp[a] = b
        addr.append(tmp)

    # Использование функции display_shortcuts и вывод результатов
    addr = []
    result = processor("Нижний Новгород " + input_text)
    referent = result.matches[0].referent
    display_shortcuts(referent)
    str = [str for dict in addr for str in dict.values()]
    for i in range(len(str)):
        output_text += str[i] + ' '

    output_text += '\n\n'
    output_text += 'Description: '
    output_text += input_text
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


client = telegram_parser(session, api_id, api_hash, telegram_channels, parse_func=parse_func, loop=loop)

try:
    client.run_until_disconnected()
except Exception as e:
    message = f'&#9888; ERROR: telegram parser (all parsers) is down! \n{e}'
finally:
    loop.close()
