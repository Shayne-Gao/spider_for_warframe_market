rm -f ../output/*
ls_date=`date +%Y%m%d`
scrapy crawl wm_spider -o ../output/${ls_date}.csv
sz ../output/${ls_date}.csv 
