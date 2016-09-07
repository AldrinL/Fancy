import urllib.request
import http.cookiejar
from bs4 import BeautifulSoup
import re, os
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from pymongo import *

app = Flask(__name__)
Bootstrap(app)

def get_opener(head):
    # deal with the Cookies
    cj = http.cookiejar.CookieJar()
    pro = urllib.request.HTTPCookieProcessor(cj)
    opener = urllib.request.build_opener(pro)
    header = []
    for key, value in head.items():
        elem = (key, value)
        header.append(elem)
    opener.addheaders = header
    return opener

def get_links():
    head = {
            'Connection': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64;         Trident/7.0; rv:11.0) like Gecko'
        }
    opener = get_opener(head)
    rep = opener.open('http://www.smzdm.com')
    soup = BeautifulSoup(rep.read(), "html.parser")
    tags = soup('a')
    links = set()
    for tag in tags:
        link = tag.get('href', None)
        if link and re.search("http://www.smzdm.com/p/\d{7}/$", link):
            links.add(link)
    return links

def get_info(links):
    head = {
            'Connection': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64;         Trident/7.0; rv:11.0) like Gecko'
        }
    i=0

    opener = get_opener(head)
    itemlist= []
    for link in links:
        print('processing ', link)
        rep = opener.open(link)
        soup = BeautifulSoup(rep.read(), "html.parser")
        title=soup.find("h1", class_="article_title ")
        info = {}
        if title and soup.find("div", class_="buy"):
            info['price'] = title.find('span').text
            info['title'] = title.text
            info['buylink'] = soup.find("div", class_="buy").a.get('href')
            info['worthy_num'] = int(soup.find('span',id="rating_worthy_num").text.strip())
            info['unworthy_num']=int(soup.find('span',id="rating_unworthy_num").text.strip())
            if info['unworthy_num'] > 5 and info['worthy_num'] + info['unworthy_num'] >10:
                info['worthrate'] = info['worthy_num']/(info['worthy_num'] + info['unworthy_num'])
            info['collected'] = soup.find('a',class_='fav').em.text
            info['imglink'] = soup.find('a',class_="pic-Box").img.get('src')
            info['brief'] = ''
            if soup.find('div',class_="inner-block"):
                info['brief'] += str(soup.find('div',class_="inner-block").p)
            if soup.find('div',class_="baoliao-block"):
                info['brief'] += str(soup.find('div',class_="baoliao-block").p)
            item = {'link' : link, 'info': info}
            itemlist.append(item)
            print(item, ' processed')
        i+=1
        print(i, 'done,',len(links) - i ,'remaining')
        if i >= 20:
            return itemlist
    print('信息收集完毕')
    return itemlist

@app.before_first_request
def update():
    client = MongoClient(os.environ.get('DATABASE_URL'))
    db = client.fanci
    item_collection = db.item
    if not item_collection.find_one():
        itemlist = get_info(get_links())
        item_collection.insert_many(itemlist)
        print('信息已写入数据库')
    else:
        print('数据库已存在信息')

@app.route('/')
def index():
    client = MongoClient(os.environ.get('DATABASE_URL'))
    # client = MongoClient()
    db = client.fanci
    item_collection = db.item
    items = item_collection.find()
    print('正从数据库取出信息')
    return render_template('index.html', items = items)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port = 3000)
