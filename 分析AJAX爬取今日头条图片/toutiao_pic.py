import os
import requests
from hashlib import md5
from multiprocessing.pool import Pool
from urllib.parse import urlencode


BASE_DIR = os.getcwd()
GROUP_START = 1
GROUP_END = 2


def get_page(offset):
    params = {
        'offset': offset,
        'format': 'json',
        'keyword': '帅哥',
        'autoload': 'true',
        'count': '20',
        'cur_tab': '1',
        'from': 'search_tab'
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(params)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError:
        return None


def get_image(json):
    data = json.get('data')
    if data:
        for item in data:
            title = item.get('title')
            if item.get('image_list'):
                for image in item.get('image_list'):
                    yield {
                        'image': 'http:' + image.get('url'),
                        'title': title
                    }


def save_image(item):
    large_image_url = item.get('image').replace('list', 'large')
    if not os.path.exists(BASE_DIR + '/image/' + item.get('title')):
        os.makedirs(BASE_DIR + '/image/' + item.get('title'))
    try:
        response = requests.get(large_image_url)
        if response.status_code == 200:
            file_path = BASE_DIR + '/image/{0}/{1}.{2}'.format(
                   item.get('title'), md5(response.content).hexdigest(), 'jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            else:
                print('Already Downloaded', file_path)
    except requests.ConnectionError:
        print('Failed to save image')


def main(offset):
    json = get_page(offset)
    for item in get_image(json):
        print(item)
        save_image(item)


if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 20 for x in range(GROUP_START, GROUP_END + 1)])
    pool.map(main, groups)
    pool.close()
    pool.join()
