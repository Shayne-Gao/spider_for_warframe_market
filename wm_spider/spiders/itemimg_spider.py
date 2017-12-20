#!/usr/bin/python
# -*- coding:utf-8 -*- 

import scrapy
import json
import urlparse
import HTMLParser
import ConfigParser
import os
import urllib
import time
import MySQLdb
import cgi

#rewrite conf class to avoid lower()
class myconf(ConfigParser.ConfigParser):  
    def __init__(self,defaults=None):  
        ConfigParser.ConfigParser.__init__(self,defaults=None)  
    def optionxform(self, optionstr):  
        return optionstr  

#从huijiwiki抓取mod的图片url放入数据库
class WmSpider(scrapy.Spider):
    name = "itemimg"
    itemName = "";

    db = None
    cursor = None
    #def __init__(self, role="BeastMastery",kmin=15,kmax=20, *args, **kwargs):
    #def __init__(self,role,kmin,kmax):
     
    def recFormat(self,l):
        resStr = '%s:%sx%s|'%(l['ingame_name'],l['price'],l['count'])
        return resStr

    def start_requests(self):
        self.db = MySQLdb.connect("localhost","root","IWLX8IS12Rl","warframe",charset='utf8' )
        self.cursor = self.db.cursor()
        
        itemNames = self.getInfoFromDb()
        for item in itemNames:
            url = "http://warframe.huijiwiki.com/wiki/"+item['name_zh']+"?"+str(item['id'])
            print url
            yield scrapy.Request(url=url, callback=self.parse)
        

    def getInfoFromDb(self):
        sql = """SELECT id,name_zh from item where type="Mod" """
        #sql = """SELECT id,name_zh FROM item WHERE TYPE='Void Trader' AND name_zh LIKE '%Prime'"""
          # 执行SQL语句
        self.cursor.execute(sql)
        # 获取所有记录列表
        results = self.cursor.fetchall()
        resList = []
        #print results
        if len(results)==0:
            return resList
        for r in results:
            temp = {}
            temp['id']=r[0]
            temp['name_zh']=r[1]
            
            resList.append(temp)
        return resList

 

    def insertDB(self,name,type,buildId):
        sql = """INSERT INTO build_item (name_en,item_type,build_id) VALUES ('%s',%s,'%s') """%(name,type,buildId)
        try:
           # 执行sql语句
           print sql
           #self.cursor.execute(sql)
           # 提交到数据库执行
           self.db.commit()
        except:
           # Rollback in case there is any error
           self.db.rollback()

    def updateDB(self,itemId,imgpath):
        sql = """UPDATE item SET item_img = '%s' WHERE id = '%s' """%(imgpath,itemId)
        try:
           # 执行sql语句
           print sql
           self.cursor.execute(sql)
           # 提交到数据库执行
           self.db.commit()
        except:
           # Rollback in case there is any error
           self.db.rollback()

    def parse_mod_map(self,response):
        r=response.xpath("//*[@id='conteneur-liste-mods-2']/div")
        for rs in r:
            id = rs.xpath('@data-id').extract_first()
            name = rs.xpath('@data-nom').extract_first()
            print """'%s':'%s',"""%(id,name)
    def parse(self, response):
        r = response.xpath("//*[@id='mw-content-text']/table[1]/tr[2]/td/img/@src").extract_first()
        if r == None:
            r=response.xpath("//*[@id='mw-content-text']/table[2]/tr[2]/td/img/@src").extract_first()
        itemName = response.url
        url = str(response.url)
        urlInfos = url.split('?')
        itemId = urlInfos[-1]
        self.updateDB(itemId,r)
        return None

    


