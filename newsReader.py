import asyncio
import requests
from bs4 import BeautifulSoup
import time
from shuttleai import *
# from models import News
# from django.http import JsonResponse

import g4f

from g4f.Provider import (
    Bard,
    Bing,
    HuggingChat,
    OpenAssistant,
    OpenaiChat,
)

# Сделаю ветку с django которая не работает друзья

news_limit = 5
SHUTTLE_KEY = "shuttle-rkxlqhwgdbjug0jcidvf"

prompt = """На русском языке:
        Укажите только место события: только существующий город, улица, дом, и исключите излишние локационные детали. Если адрес за пределами Нижегородской области, то ставить Нижний Новгород без других указаний места.
    """

async def parsing_func(input_text):
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
        return response['choices'][0]['message']['content']


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

# вот тут вообще не понял как это должно работать друзья
# def add_to_database(request):
#     if request.method == 'POST':
#         id = request.POST.get('id')
#         title = request.POST.get('title')
#         description = request.POST.get('description')
#         date = request.POST.get('date')
#         place = request.POST.get('place')
#         url = request.POST.get('url')
#         img = request.POST.get('img')
#
#         new_data = News(id=id, title=title, description=description, date=date, place=place, url=url, img=img)
#         new_data.save()
#
#         return JsonResponse({'message': 'Data added to database'})
#     else:
#         return JsonResponse({'error': 'Error'}, status=405)

# def pass_news(id, title, description, date, place, url, img):
#     server = 'http://kerilserver.com/add_data/'  # адрес сервера Керила
#     news = {
#         'id': id,
#         'title': title,
#         'description': description,
#         'date': date,
#         'place': place,
#         'url': url,
#         'img': img
#     }
#
#     response = requests.post(server, data=news)
#     print(response.json())


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

        date = get_after_find(article, 'time', 'datetime')
        url = 'https://www.nn.ru/' + article.a['href']
        img = get_after_find(article, 'img', 'src')

        response = requests.get(url)
        news_data = BeautifulSoup(response.text, 'html.parser')
        text = title
        if news_data.find('div', {'class': 'qQq9J'}) is not None:
            text += ". " + news_data.find('div', {'class': 'qQq9J'}).get_text(strip=True)

        place = await parsing_func(text)

        print(title, '\n', text, '\n', date, '\n', place, '\n', url, '\n', img, '\n\n\n')
        time.sleep(10)
        #pass_news(0, title, '', date, '', url, img)

async def rbc():
    site_url = 'https://nn.rbc.ru/nn/'
    data = check_response(site_url)
    if data is None:
        return

    for article in data.find_all('div', {'class': 'item js-rm-central-column-item item_image-mob js-category-item'})[:news_limit]:
        title = article.find('span', {'class': 'normal-wrap'}).text
        date = article.find('span', {'class': 'item__category'}).text
        url = article.find('a', {'class': 'item__link rm-cm-item-link js-rm-central-column-item-link'}).get('href')
        img = get_after_find(article, 'img', 'src')

        response = requests.get(url)
        news_data = BeautifulSoup(response.text, 'html.parser')
        text = ''
        if news_data.find('div', {'class': 'article__text__overview'}) is not None:
            text = news_data.find('div', {'class': 'article__text__overview'}).get_text(strip=True)

        place = await parsing_func(text)

        print(title, '\n', text, '\n', date, '\n', place, '\n', url, '\n', img, '\n\n\n')
        time.sleep(10)
        # pass_news(0, title, '', date, '', url, img)

while True:
    print("NN.RU:\n")
    asyncio.run(nnru())
    print("RBC:\n")
    asyncio.run(rbc())
    time.sleep(600)
