import requests
from bs4 import BeautifulSoup
import time
from models import News
from django.http import JsonResponse
import psycopg2

# conn = psycopg2.connect(host="localhost", dbname="nnru_reader", user="postgres", password="postgres")
# cur = conn.cursor()

news_limit = 3

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
def add_to_database(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        text = request.POST.get('text')
        date = request.POST.get('date')
        coord_x = request.POST.get('coord_x')
        coord_y = request.POST.get('coord_y')
        url = request.POST.get('url')
        img = request.POST.get('img')

        new_data = News(id=id, date=date, coord_x=coord_x, coord_y=coord_y, url=url, img=img)
        new_data.save()

        return JsonResponse({'message': 'Данные успешно добавлены в базу данных'})
    else:
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)


def pass_news(id, text, date, coord_x, coord_y, url, img):
    server = 'http://kerilserver.com/add_data/'  # адрес сервера Керила
    news = {
        'id': 0,
        'text': text,
        'date': date,
        'coord_x': 0.0,
        'coord_y': 0.0,
        'url': url,
        'img': img
    }

    response = requests.post(server, data=news)
    print(response.json())

def rbc():
    url = 'https://nn.rbc.ru/nn/'
    data = check_response(url)
    if data is None:
        return


    for article in data.find_all('div', {'class': 'item js-rm-central-column-item item_image-mob js-category-item'})[:news_limit]:
        title = article.find('span', {'class': 'normal-wrap'}).text
        date = article.find('span', {'class': 'item__category'}).text
        url = article.find('a', {'class': 'item__link rm-cm-item-link js-rm-central-column-item-link'}).get('href')
        img = get_after_find(article, 'img', 'src')

        print(title, '\n', date, '\n', url, '\n', img, '\n\n\n')
        pass_news(0, title, date, 0.0, 0.0, url, img)




def nnru():
    url = 'https://www.nn.ru/text/'
    data = check_response(url)
    if data is None:
        return

    for article in data.find_all('article', class_='OPHIx')[:news_limit]:
        title = None
        tag = article.find('h2')
        if tag:
            title = tag.a['title']
        date = get_after_find(article, 'time', 'datetime')
        url = 'https://www.nn.ru/' + article.a['href']
        img = get_after_find(article, 'img', 'src')

        print(title, '\n', date, '\n', url, '\n', img, '\n\n\n')
        pass_news(0, title, date, 0.0, 0.0, url, img)




while True:
    print("NN.RU:\n")
    nnru()
    print("RBC:\n")
    rbc()
    time.sleep(60)

# cur.close()
# conn.close()
