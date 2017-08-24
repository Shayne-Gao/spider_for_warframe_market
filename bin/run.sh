#rm -f ../output/*
ls_date=`date +%Y%m`
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
mkdir ${DIR}/../output
mkdir ${DIR}/../log
nohup scrapy crawl wm_spider -o ${DIR}/../output/${ls_date}.csv -s LOG_FILE=${DIR}/../log/${ls_date}.log 
#sz ../output/${ls_date}.csv 
