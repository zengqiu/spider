#!/usr/bin/env python
#encoding: utf-8
#author: zengqiu

import urllib2
import urllib
from BeautifulSoup import BeautifulSoup
import re
import urlparse
import os

image_path = "/home/mini/wallbase"

def spider(url):
    user_agent = "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)"
    headers = {'User-Agent': user_agent}
    request = urllib2.Request(url, headers = headers)
    response = urllib2.urlopen(request)
    soup = BeautifulSoup(response.read())
    results = []
    
    for thumb in soup.findAll("img", attrs={"class": re.compile("file"), "data-original": True}):
        thumb_parent = thumb.findParent("a")
        #print thumb_parent['href']
        result = spider_image(thumb_parent['href'])
        results.append(result)

    return results

def spider_image(url):
    user_agent = "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)"
    headers = {'User-Agent': user_agent}
    request = urllib2.Request(url, headers = headers)
    response = urllib2.urlopen(request)
    soup = BeautifulSoup(response.read())
    result = {}

    img = soup.findAll("img", attrs={"class": re.compile("wall")}, limit=1)
    result['url'] = img[0]['src']
    
    for size in soup.findAll("div", "l1"):
        if size.parent.name == "a":
            result['size'] = size.text
            break
    
    return result

def download(url, path):
    filename = re.split('/', urlparse.urlparse(url).path)[-1]
    filepath = os.path.join(path, filename)
    
    if not os.path.isfile(filepath):
        urllib.urlretrieve(url, filepath)

def makedir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def run():
    page = 0
    enable = True
    
    while enable:
        url = "http://wallbase.cc/toplist/%d" % page
        results = spider(url)
        if results:
            for result in results:
                subpath = result['size']
                newpath = os.path.join(image_path, subpath)
                makedir(newpath)
                download(result['url'], newpath)
                
            page += 32
        else:
            enable = False

def main():
    print 'Please use it as ./wallbase'
    run()

if __name__ == '__main__':
    main()