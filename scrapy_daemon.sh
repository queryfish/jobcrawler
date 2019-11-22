until `scrapy crawl $1 --logfile ./logs/$1$(date +%Y%m%d%H).log --loglevel INFO`;
do
    echo "$(date):Server 'myserver' crashed with exit code $?.  Respawning.." >&2
    sleep 60
done

# echo $1 $(date +%Y%m%d_%H)
