import scrapy
import json
import urlparse
import HTMLParser
import ConfigParser
import os
import urllib
import time

#rewrite conf class to avoid lower()
class myconf(ConfigParser.ConfigParser):  
    def __init__(self,defaults=None):  
        ConfigParser.ConfigParser.__init__(self,defaults=None)  
    def optionxform(self, optionstr):  
        return optionstr  

class WmSpider(scrapy.Spider):
    name = "wm_spider"
    itemName = "";
    #def __init__(self, role="BeastMastery",kmin=15,kmax=20, *args, **kwargs):
    #def __init__(self,role,kmin,kmax):
     
    def recFormat(self,l):
        resStr = u'[%s:%sx%s]'%(l['ingame_name'],l['price'],l['count'])
        return resStr

    def start_requests(self):
       
        baseUrl = "http://warframe.market/api/get_orders/"
        urls = []
        conf = myconf()
        path = os.path.split(os.path.realpath(__file__))[0] + '/../../conf/wm.cfg'
        conf.read(path)
      
        cates = ["Set","Blueprint"]
        for cate in cates:
            items = conf.options(cate) 
            for item in items:
                urls.append(baseUrl+str(cate) + "/" +str(item))
                self.itemName = item
                pass
       
     
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

  

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
        res['item'] =   urllib.unquote(urlInfos[6])
        #get other info
        res['top_rec'] = []    
        for i in range(0,3):
            strT = self.recFormat(onlineSellRec[i])
            res['top_rec'].append(strT)  
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
        return res

    
