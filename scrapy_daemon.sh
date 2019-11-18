until `scrapy crawl dbbCrawler --logfile ./logs/rulespider201911.log --loglevel INFO`;
do
    echo "$(date):Server 'myserver' crashed with exit code $?.  Respawning.." >&2
    sleep 60
done
