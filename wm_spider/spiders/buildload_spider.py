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

#rewrite conf class to avoid lower()
class myconf(ConfigParser.ConfigParser):  
    def __init__(self,defaults=None):  
        ConfigParser.ConfigParser.__init__(self,defaults=None)  
    def optionxform(self, optionstr):  
        return optionstr  

class WmSpider(scrapy.Spider):
    name = "buildload"
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
        
        baseUrls =[ "http://warframe-builder.com/Primary_Weapons/Builder/Lenz","http://warframe-builder.com/Secondary_Weapons/Builder/Akjagara","http://warframe-builder.com/Melee_Weapons/Builder/Cronus"]
        for url in baseUrls:
            print url
            yield scrapy.Request(url=url, callback=self.parse_mod_map)
        

    def getInfoFromDb(self,itemName):
        sql = """SELECT id,name_en,type from item where name_zh like '%%%s%%' or name_en like '%%%s%%' """ %(itemName,itemName)
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
            temp['name_en']=r[1]
            temp['type']=r[2]
            resList.append(temp)
        return resList

 

    def insertDB(self,name,type,buildId):
        sql = """INSERT INTO build_item (name_en,item_type,build_id) VALUES ('%s',%s,'%s') """%(name,type,buildId)
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
        r= response.xpath("//*[@id='liste_armes']/option/@value").extract()
        for rs in r:
            t=rs.split('*')
            if len(t)<2:
                continue
            id = t[1]
            name = t[0].replace('_',' ').replace('prime','Prime')
            self.insertDB(name,4,id)
        return None

    


