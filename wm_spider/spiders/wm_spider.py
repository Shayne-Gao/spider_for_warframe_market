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
    name = "wm_spider"
    itemName = "";

    db = None
    cursor = None
    #def __init__(self, role="BeastMastery",kmin=15,kmax=20, *args, **kwargs):
    #def __init__(self,role,kmin,kmax):
     
    def recFormat(self,l):
        resStr = '%s:%sx%s|'%(l['ingame_name'],l['price'],l['count'])
        return resStr
    #从cfg文件中读取需要爬的物品，然后从wm中爬取这个物品的价格，放入mysql
    def start_requests(self):
        self.db = MySQLdb.connect("localhost","root","IWLX8IS12Rl","warframe",charset='utf8' )
        self.cursor = self.db.cursor()
 
        
        baseUrl = "http://warframe.market/api/get_orders/"
        urls = []
        conf = myconf()
        path = os.path.split(os.path.realpath(__file__))[0] + '/../../conf/wm.cfg'
        conf.read(path)
     
        items = conf.options('Item') 
        for item in items:
            wholeNameList = self.getInfoFromDb(item)
            for itemInfo in wholeNameList:
                urls.append(baseUrl+str(itemInfo['type']) + "/" +str(itemInfo['name_en']) + "?"+str(itemInfo['id'] ) )
                
     
        for url in urls:
            print url
            yield scrapy.Request(url=url, callback=self.parse)

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

    def insertDb(self,content):
        #get item id
     
        sql = """INSERT INTO item_price_record (item_id,name_en,type, cheapest_price,top_avg,top_count,all_avg,all_count,record_time,top_rec)
                 VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')
                 """%(content['itemId'],content['item'],content['category'],content['cheapest_price'],content['top_avg'],content['top_count'],content['all_avg'],content['all_count'],content['record_time'],content['top_rec'])
        try:
           # 执行sql语句
           print sql
           self.cursor.execute(sql)
           # 提交到数据库执行
           self.db.commit()
        except:
           # Rollback in case there is any error
           self.db.rollback()

    def parse(self, response):
        jsonInfo = response.xpath("//text()").extract_first()
        data = json.loads(jsonInfo)
        sellInfo = data['response']['sell'];
        #get online player records
        onlineSellRec = []
        onlineSellRecSum = 0
        onlineSellRecCount = 0
        for info in sellInfo:
            if info['online_ingame'] == False:
                continue
            #ignore xbox and ps4 record
            nameStr = info['ingame_name'].encode("utf-8")
            nameStr = urllib.unquote(nameStr)
            if nameStr.startswith('(PS4)') or nameStr.startswith('(XB1)'):
                continue
            #else
            onlineSellRec.append(info)
            onlineSellRecSum += info['price'] * info['count']
            onlineSellRecCount += info['count']
        #sort and analysis
        onlineSellRec.sort(key=lambda obj:obj.get('price'), reverse=False)
        res = {}
        #get item name from url
        url = str(response.url)
        urlInfos = url.split('/')
        res['category'] = urlInfos[5]
        itemAndId =   urllib.unquote(urlInfos[6]).split('?')
        res['item'] = itemAndId[0]
        res['itemId'] = itemAndId[1]

        #get other info
        res['top_rec'] = ""    
        for i in range(0,3):
            strT = self.recFormat(onlineSellRec[i])
            res['top_rec'] += strT
        res['cheapest_price'] = onlineSellRec[0]['price']
        res['all_count'] = onlineSellRecCount
        res['all_avg'] = onlineSellRecSum / onlineSellRecCount

        topSum = 0
        topCount = 0
        for rec in onlineSellRec[0:20]:
            topSum += rec['price'] * rec['count']
            topCount += rec['count']
        res['top_count'] = topCount
        res['top_sum'] = topSum
        res['top_avg'] = topSum / topCount
        res['record_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        self.insertDb(res)
        return res

    


