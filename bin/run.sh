#rm -f ../output/*
mkdir ../output
mkdir ../log
ls_date=`date +%Y%m`
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
nohup scrapy crawl wm_spider -o ${DIR}/../output/${ls_date}.csv -s LOG_FILE=${DIR}/../log/${ls_date}.log 
#sz ../output/${ls_date}.csv 
