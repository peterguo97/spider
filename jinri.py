import requests
from urllib.parse import urlencode
from requests.exceptions import RequestException
import json
import pymongo
from bs4 import BeautifulSoup
import re
from config import *
import os
from hashlib import md5
from multiprocessing import Pool

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

def get_image_index(offset,keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': '3',
        'from': 'search_tab'
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    print(url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('解析出错')
        return None

def parse_image_url(html):
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('article_url')

def get_image_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求详情页解析出错')
        return None

def parse_page_detail(html,url):
    soup = BeautifulSoup(html,'lxml')
    title = soup.select('title')[0].get_text()
    image_pattern = re.compile('gallery: JSON.parse\((.*?)\)',re.S)
    result = re.search(image_pattern, html)
    if result:
        res = json.loads(json.loads(result.group(1)))
        if res and 'sub_images' in res:
            sub_images = res.get('sub_images')
            images = [ item.get('url') for item in sub_images]
            return {
                'title': title,
                'url': url,
                'images': images
            }
def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('存储到mongoDB',result)
        return True
    return False



def save_image(url):
    print('正在下载', url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
             content = response.content
    except RequestException:
        print('下载图片出错', url)
    file_path = '{0}/{1}.{2}'.format(os.getcwd(),md5(content).hexdigest(),'jpg')
    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            f.write(content)
            f.close()

def main(offset):
    html = get_image_index(offset, '街拍')
    for url in parse_image_url(html):
        detail = get_image_detail(url)
        if detail:
            result = parse_page_detail(detail, url)
            if result:
                save_to_mongo(result)
                for item in result['images']:
                    save_image(item)


if __name__ == '__main__':
    groups = [x*20 for x in range(GROUP_START,GROUP_END)]
    pool = Pool()
    pool.map(main,groups)
    
