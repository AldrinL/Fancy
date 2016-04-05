import urllib.request
import http.cookiejar
from bs4 import BeautifulSoup
import re

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
    j=0
    errer=set()
    opener = get_opener(head)
    for link in links:
        # print(link)
        rep = opener.open(link)
        soup = BeautifulSoup(rep.read(), "html.parser")
        title=soup.find("h1", class_="article_title ")
        try:
            if title:       
                price = title.find('span').text
                title = title.text
                buylink = soup.find("div", class_="buy").a.get('href')
                worthy_num=soup.find('span',id="rating_worthy_num").text.strip()
                unworthy_num=soup.find('span',id="rating_unworthy_num").text.strip()
                collected = soup.find('a',class_='fav').em.text
                imglink = soup.find('a',class_="pic-Box").img.get('src')
                brief = ''
                if soup.find('div',class_="inner-block"):
                    brief += str(soup.find('div',class_="inner-block").p)
                if soup.find('div',class_="baoliao-block"):
                    brief += str(soup.find('div',class_="baoliao-block").p)
                    print(str(brief))
                    j+=1
        # print(title, price, worthy_num, unworthy_num, collected)
                else:
                    i+=1
                    print(link)
                    errer.add(link)
        except:
            print(link)
    print(i,j,errer)