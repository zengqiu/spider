#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: zengqiu

# 美拍视频下载

import sys
import os
import re
import urlparse
import urllib
import urllib2
import shutil
from BeautifulSoup import BeautifulSoup

path_ts = 'E:\\Share\\ts'
url_prefix = 'http://media-pili.1iptv.com'
url_web = 'http://www.meipai.com/media/575186182'

def find_text(reg, text):
    result = re.findall(reg, text)
    return result

def get_m3u8(url):
    reg = "[\'](.*?)[\']"
    user_agent = "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)"
    headers = {'User-Agent': user_agent}
    request = urllib2.Request(url, headers = headers)
    response = urllib2.urlopen(request)
    # print response.read()
    soup = BeautifulSoup(response.read())
    for content in soup.findAll("script"):
        for line in content.text.split('\n'):
            if 'm3u8' in line:
                result = find_text(reg, line)
                return result[0]

def file_handler(filename):
    list_ts = list()
    list_url = list()
    with open(filename, 'r') as f:
        for line in f:
            if line[0] != '#':
                url = url_prefix + line.strip()
                list_url.append(url)
                list_ts.append(line.split('/')[-1].strip())
    # print list_ts
    # print list_url
    return {'url': list_url, 'ts': list_ts}

def download(url, path):
    filename = re.split('/', urlparse.urlparse(url).path)[-1]
    filepath = os.path.join(path, filename)
    
    if not os.path.isfile(filepath):
        urllib.urlretrieve(url, filepath)

    return filename

def clear_dir(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception, e:
            print e

def main():
    url_m3u8 = get_m3u8(sys.argv[1])
    file_m3u8 = download(url_m3u8, path_ts)
    # print file_m3u8
    
    data = file_handler(os.path.join(path_ts, file_m3u8))
    list_url = data['url']
    list_ts = data['ts']
    
    for url in list_url:
        download(url, path_ts)

    file_merged = file_m3u8.split('.')[0] + '.ts'
    # print file_merged
    with open(file_merged, 'wb') as merged:
        for ts in list_ts:
            with open(os.path.join(path_ts, ts), 'rb') as mergefile:
                shutil.copyfileobj(mergefile, merged)

    clear_dir(path_ts)

if __name__ == '__main__':
    main()