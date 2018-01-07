import requests
import os
from bs4 import BeautifulSoup
headers = {'Accept':' text / html, application / xhtml + xml, application / xmlq = 0.9, image / webp, image / apng, * / *q = 0.8',
           'Referer': 'http://www.mzitu.com/115030',
           'Cookie': 'Hm_lvt_dbc355aef238b6c32b43eacbbf161c3c=1515305661,1515319710;Hm_lpvt_dbc355aef238b6c32b43eacbbf161c3c = 1515329314',
           'Host': 'www.mzitu.com',
           'User-Agent': 'Mozilla / 5.0 (Windows NT 10.0;WOW64) AppleWebKit / 537.36 (KHTML, like Gecko) Chrome / 62.0.3202.94 Safari / 537.36'
           }
all_url = 'http://www.mzitu.com/all'
start_html = requests.get(all_url, params = headers)
Soup = BeautifulSoup(start_html.text, 'lxml')
all_a = Soup.find('div',class_='all').find_all('a')
for a in all_a:
    href = a['href']
    title = a.get_text()
    path = str(title).strip()
    os.makedirs(os.path.join("D:\mzitu",path))
    os.chdir("D:\mzitu\\"+path)
    res = requests.get(href, params=headers)
    Detail_html = BeautifulSoup(res.text, 'lxml')
    count = Detail_html.select('.pagenavi span')
    if count:
        pagelen = count[-2].get_text()
        for page in range(1,int(pagelen)+1):
            page_url = href+'/'+str(page)
            image_res = requests.get(page_url,params=headers)
            image_html = BeautifulSoup(image_res.text,'lxml')
            image_url = image_html.find('div',class_="main-image").find("img")['src']
            print('正在下载图片%s' %image_url)
            name = image_url[-9:-4]
            img = requests.get(image_url,params=headers)
            f = open(name+ '.jpg','ab')
            f.write(img.content)
            f.close()
