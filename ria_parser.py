import requests
from bs4 import BeautifulSoup
import time
import datetime
from typing import List, Dict, Any
import json
import csv
import re
import schedule
# import pandas as pd


# Сегодняшний день
today = str(datetime.datetime.today())

# Преобразуем сегодняшний день для выполнения запроса
date = "".join(today.split("-"))

# Ссылка на страницу новостей
url = "https://ria.ru/services/politics/more.html"

# params & headers для выполнения запроса
params = {
    "id": "1869469542",
    "date": date
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,ru;q=0.8,af;q=0.7"
}

# Ключевые слова поиска новостей (как пример, взял США, но можно добавить еще)
keywords = ["США"]

def extract_article_title(article_url: str) -> Dict[str, Any]:
    pass

def download_news():
    pass


schedule.every(24).hours.do(download_news)

while True:
    schedule.run_pending()
    time.sleep(1)
