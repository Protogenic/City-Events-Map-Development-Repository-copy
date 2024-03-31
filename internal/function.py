import base64

import requests
from shuttleai import ShuttleAsyncClient
from requests.auth import HTTPBasicAuth
from config.config import SHUTTLE_KEY, prompt


async def SummarizeAiFunc(input_text):
    async with ShuttleAsyncClient(SHUTTLE_KEY, timeout=60) as shuttle:
        response = await shuttle.chat_completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": input_text + prompt}],
            stream=False,
            plain=False,
            internet=False,
            max_tokens=100,
            temperature=0.5,
        )
        return response.choices[0].message.content


def filter_func(string):
    words = string.lower().split()
    key_words = [
        "реклам",
        "розыгрыш",
        "друз",
        "рекоменд",
        "показ",
        "бесплат",
        "кешбек",
        " мы "
        "Телеграмм"
        "работаем"
        "кто"
        "своё"
        "билеты"
    ]
    for word in words:
        for key in key_words:
            if key in word:
                return False
    return True


auth = HTTPBasicAuth('admin', 'admin')


def response_to_server(post):
    response_post = requests.post(url='https://api.in-map.ru/api/news/', json=post, auth=auth)
    print("POST-запрос:", response_post.json())
