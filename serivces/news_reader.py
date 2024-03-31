import asyncio
import base64

import requests
from PIL import Image
from io import BytesIO
import time
import json
from datetime import datetime
from bs4 import BeautifulSoup
from internal.function import response_to_server, filter_func, SummarizeAiFunc

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Django_config.settings")

news_limit = 9


def get_after_find(article, par1, par2):
    tag = article.find(par1)
    if tag:
        return tag[par2]
    else:
        return None


def check_response(url):
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        return BeautifulSoup(html, 'html.parser')
    else:
        print('Failed to send request. Status code:', response.status_code)
        return None


def download_image(url, save_path):
    response = requests.get(url)

    if response.status_code == 200:
        image_content = response.content
        image = Image.open(BytesIO(image_content))
        image.save(save_path)
        return image
    else:
        print("Error downloading image")
        return None


async def send_json(img, text, url):
    today = datetime.today()
    date = today.strftime('%Y-%m-%d')

    img_path = "images/" + os.path.basename(img)
    download_image(img, img_path)
    with open(img_path, "rb") as file:
        image_data = file.read()
        img = base64.b64encode(image_data).decode('utf-8')

    post = await SummarizeAiFunc(text)
    data = json.loads(post)
    data['url'] = url
    data['img'] = img
    data['news_date'] = date
    response_to_server(data)


async def nnru():
    site_url = 'https://www.nn.ru/text/'
    data = check_response(site_url)
    if data is None:
        return

    for article in data.find_all('article', class_='OPHIx')[:news_limit]:

        rubrics = article.find_all(attrs={"slot": "rubrics"})
        city_news = False
        for r in rubrics:
            if r['title'] == 'Город' or r['title'] == 'Дороги и транспорт':
                city_news = True

        if not city_news:
            continue

        title = None
        tag = article.find('h2')
        if tag:
            title = tag.a['title']

        url = 'https://www.nn.ru/' + article.a['href']
        img = get_after_find(article, 'img', 'src')

        response = requests.get(url)
        news_data = BeautifulSoup(response.text, 'html.parser')
        text = title
        if news_data.find('div', {'class': 'qQq9J'}) is not None:
            text += ". " + news_data.find('div', {'class': 'qQq9J'}).get_text(strip=True)

        await send_json(img, text, url)


month_names = {
        'янв': '01',
        'фев': '02',
        'мар': '03',
        'апр': '04',
        'май': '05',
        'июн': '06',
        'июл': '07',
        'авг': '08',
        'сен': '09',
        'окт': '10',
        'ноя': '11',
        'дек': '12'
    }

async def rbc():
    site_url = 'https://nn.rbc.ru/nn/'
    data = check_response(site_url)
    if data is None:
        return

    for article in data.find_all('div', {'class': 'item js-rm-central-column-item item_image-mob js-category-item'})[:news_limit]:
        title = article.find('span', {'class': 'normal-wrap'}).text
        url = article.find('a', {'class': 'item__link rm-cm-item-link js-rm-central-column-item-link'}).get('href')
        img = get_after_find(article, 'img', 'src')

        response = requests.get(url)
        news_data = BeautifulSoup(response.text, 'html.parser')
        text = ''
        if news_data.find('div', {'class': 'article__text__overview'}) is not None:
            text = news_data.find('div', {'class': 'article__text__overview'}).get_text(strip=True)

        await send_json(img, text, url)


def run():
    print("NN.RU:\n")
    asyncio.run(nnru())
    print("RBC:\n")
    #asyncio.run(rbc())
