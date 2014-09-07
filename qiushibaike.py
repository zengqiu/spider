#!/usr/bin/env python
#encoding: utf-8
#author: zengqiu

import urllib2
import urllib
from BeautifulSoup import BeautifulSoup
import MySQLdb
import datetime
import re
import urlparse
import os

mysql_host = "localhost"
mysql_port = 3306
mysql_user = "root"
mysql_password = "zengqiu"
mysql_db_name = "qiushibaike"
mysql_table_name = "qiushibaike"
image_path = "/home/mini/qiushibaike"

def spider(url):
    user_agent = "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)"
    headers = {'User-Agent': user_agent}
    request = urllib2.Request(url, headers = headers)
    response = urllib2.urlopen(request)
    soup = BeautifulSoup(response.read())
    results = []
    for content in soup.findAll("div", "content", title=True):
        result = {}
        result['content'] = content.text
        #print content.text

        thumb = content.findNext("div")
        if thumb.attrs[0][1] == "thumb":
            for attr in thumb.a.img.attrs:
                if attr[0] == "src":
                    url_img = attr[1]
                    result['image'] = url_img
                    #print url_img

        for attr in content.attrs:
            if attr[0] == "title":
                date = attr[1]
                result['date'] = date
                #print date

        results.append(result)

    #for result in results:
        #for key in result:
            #print "[%s] =" % key, result[key]

    return results

def create_database(database):
    conn = MySQLdb.connect(host=mysql_host, user=mysql_user, passwd=mysql_password, port=mysql_port)
    cur = conn.cursor()
    sql = "create database %s" % (database)
    try:
        cur.execute(sql)
        conn.commit()
    except:
        conn.rollback()

    conn.close()

def create_table(table):
    conn = MySQLdb.connect(host=mysql_host, user=mysql_user, passwd=mysql_password, db=mysql_db_name, port=mysql_port, charset="utf8")
    cur = conn.cursor()
    sql = "CREATE TABLE %s (`id` int(11) NOT NULL AUTO_INCREMENT, `content` varchar(10000) NULL, `image` varchar(1000) NULL, `date` datetime NULL, `location` varchar(1000) NULL, CONSTRAINT entry UNIQUE (`content`(200), `date`), PRIMARY KEY (`id`)) ENGINE=MyISAM DEFAULT CHARACTER SET=utf8 COLLATE=utf8_general_ci" % (table)
    try:
        cur.execute(sql)
        conn.commit()
    except:
        conn.rollback()

    conn.close()

def insert(date, content, image="", location=""):
    conn = MySQLdb.connect(host=mysql_host, user=mysql_user, passwd=mysql_password, db=mysql_db_name, port=mysql_port, charset="utf8")
    cur = conn.cursor()
    sql = "insert ignore into qiushibaike(date, content, image, location) values(%s, %s, %s, %s)"
    params = (datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S'), content, image, location)

    try:
        cur.execute(sql, params)
        conn.commit()
    except:
        conn.rollback()
        
    conn.close()

def download(url, path):
    filename = re.split('/', urlparse.urlparse(url).path)[-1]
    filepath = os.path.join(path, filename)
    
    if os.path.isfile(filepath):
        urllib.urlretrieve(url, filepath)

    return filename

def makedir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def run():
    page = 1
    enable = True

    try:
        conn = MySQLdb.connect(host=mysql_host, user=mysql_user, passwd=mysql_password, db=mysql_db_name, port=mysql_port, charset="utf8")
        conn.close()
    except:
        create_database(mysql_db_name)
        create_table(mysql_table_name)
    
    while enable:
        url = "http://www.qiushibaike.com/8hr/page/%d" % page
        results = spider(url)
        if results:
            for result in results:
                if result.has_key('image'):
                    path = image_path
                    pathname = re.split(' ', result['date'])[0]
                    newpath = os.path.join(path, pathname)
                    makedir(newpath)
                    filename = download(result['image'], newpath)
                    location = os.path.join(pathname, filename)
                    insert(result['date'], result['content'], result['image'], location)
                else:
                    insert(result['date'], result['content'])
                #for key in result:
                    #print "[%s] =" % key, result[key]
                    
            page += 1
        else:
            enable = False

def main():
    print 'Please use it as ./qiushibaike'
    run()

if __name__ == '__main__':
    main()