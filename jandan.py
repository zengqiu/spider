#!/usr/bin/env python
#encoding: utf-8
#author: zengqiu

import urllib2
import urllib
from BeautifulSoup import BeautifulSoup
import MySQLdb
import re
import urlparse
import os
import socket

mysql_host = "localhost"
mysql_port = 3306
mysql_user = "root"
mysql_password = "zengqiu"
mysql_db_name = "jandan"
mysql_table_name = "jandan"
image_path = "/home/mini/jandan"

def spider_ooxx(url):
    user_agent = "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)"
    headers = {'User-Agent': user_agent}
    request = urllib2.Request(url, headers = headers)
    response = urllib2.urlopen(request)
    soup = BeautifulSoup(response.read())
    results = []
    for content in soup.findAll("li", attrs={"id": re.compile("comment")}):
        result = {}
        result["id"] = content["id"]
        img = content.findNext("p").findNext("img")
        result["src"] = img["src"]
        #print img["src"]
        results.append(result)
        
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
    sql = "CREATE TABLE %s (`id` int(11) NOT NULL AUTO_INCREMENT, `image_remote` varchar(300) NULL, `image_local` varchar(500) NULL, CONSTRAINT entry UNIQUE (`image_remote`), PRIMARY KEY (`id`)) ENGINE=MyISAM DEFAULT CHARACTER SET=utf8 COLLATE=utf8_general_ci" % (table)
    try:
        cur.execute(sql)
        conn.commit()
    except:
        conn.rollback()

    conn.close()

def insert(table, image_remote, image_local):
    conn = MySQLdb.connect(host=mysql_host, user=mysql_user, passwd=mysql_password, db=mysql_db_name, port=mysql_port, charset="utf8")
    cur = conn.cursor()
    sql = "insert ignore into " + table + "(image_remote, image_local) values(%s, %s)"
    params = (image_remote, image_local)

    try:
        cur.execute(sql, params)
        conn.commit()
    except:
        conn.rollback()
        
    conn.close()

def download(url, path, filename):
    socket.setdefaulttimeout(30)
    filepath = os.path.join(path, filename)
    
    if not os.path.isfile(filepath):
        urllib.urlretrieve(url, filepath)

def makedir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def run():
    page = 900
    enable = True

    try:
        conn = MySQLdb.connect(host=mysql_host, user=mysql_user, passwd=mysql_password, db=mysql_db_name, port=mysql_port, charset="utf8")
        conn.close()
    except:
        create_database(mysql_db_name)
        create_table(mysql_table_name)
    
    while enable:
        url = "http://jandan.net/ooxx/page-%d" % page
        print url
        results = spider_ooxx(url)
        if results:
            for result in results:
                makedir(image_path)
                image_remote = result["src"]
                filename = result["id"] + "." + image_remote.split('.')[-1]
                image_local = os.path.join(image_path, filename)
                try:
                    download(image_remote, image_path, filename)
                    insert(mysql_table_name, image_remote, image_local)
                except:
                    print filename + " is not exist"
                    
            page += 1
        else:
            enable = False

def main():
    print 'Please use it as ./jandan'
    run()

if __name__ == '__main__':
    main()