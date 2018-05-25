import pymongo
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote
from pyquery import PyQuery as Pq

# 指定要查找商品的关键字
KEYWORD = '咖啡豆'

# 指定爬取的页面数
MAX_PAGE = 10

# MongoDB相关设置
MONGO_URL = 'localhost'
MONGO_DB = 'taobao'
MONGO_COLLECTION = 'products'

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
options = webdriver.ChromeOptions()
options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=options)
wait = WebDriverWait(browser, 10)


def index_page(page):
    print('正在爬取第{}页'.format(page))
    try:
        url = 'https://s.taobao.com/search?q=' + quote(KEYWORD)
        browser.get(url)
        if page > 1:
            input_ = wait.until(ec.presence_of_element_located(
                    (By.CSS_SELECTOR, '#mainsrp-pager div.form > input')))
            submit = wait.until(ec.element_to_be_clickable(
                    (By.CSS_SELECTOR,
                     '#mainsrp-pager div.form > span.btn.J_Submit')))
            input_.clear()
            input_.send_keys(page)
            submit.click()
        wait.until(ec.text_to_be_present_in_element(
                (By.CSS_SELECTOR,
                 '#mainsrp-pager li.item.active > span'), str(page)))
        wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
        get_products()
    except TimeoutException:
        index_page(page)


def get_products():
    html = browser.page_source
    doc = Pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('data-src'),
            'price': item.find('.price').text().replace('\n', ''),
            'deal': item.find('.deal-cnt').text(),
            'title': item.find('.title').text().replace('\n', ''),
            'shop': item.find('.shopname').text(),
            'location': item.find('.location').text()
        }
        print(product)
        save_to_mongo(product)


def save_to_mongo(result):
    # noinspection PyBroadException
    try:
        if db[MONGO_COLLECTION].insert_one(result):
            print('存储到MongoDB成功')
    except Exception:
        print('存储失败')


def main():
    for i in range(1, MAX_PAGE + 1):
        index_page(i)
    browser.close()


if __name__ == '__main__':
    main()
