import requests
import re
import json
import time
from requests.exceptions import RequestException


def get_one_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 \
            Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def parse_one_page(html):
    pattern = re.compile(
        '<em class="">(.*?)</em>.*?src="(.*?)".*?title">(.*?)</span>.*?'
        '(?:title">(.*?)</span>)?other">(.*?)</span>.*?bd.*?<p.*?>(.*?)<br>'
        '.*?(.*?)</p>.*?rating_num.*?>(.*?)</span>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            'rank': item[0].strip(),
            'image': item[1].strip(),
            'title': item[2] + item[3].replace('&nbsp;', '') +
            item[4].replace('&nbsp;', '').replace(' ', ''),
            'staff': item[5].replace('&nbsp;', '').strip(),
            'genre': item[6].replace('&nbsp;', '').strip(),
            'score': item[7].strip()
        }


def write_to_json(content):
    with open('douban_top250.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')


def main(offset):
    url = 'https://movie.douban.com/top250?start=' + str(offset) + '&filter='
    html = get_one_page(url)
    for item in parse_one_page(html):
        print(item)
        write_to_json(item)


if __name__ == '__main__':
    for i in range(10):
        main(i * 25)
        time.sleep(1)
