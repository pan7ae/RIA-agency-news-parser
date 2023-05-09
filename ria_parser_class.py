import requests
from bs4 import BeautifulSoup
import time
import datetime
from typing import List, Dict, Any
import json
import csv
import re
import schedule

# Ссылка на страницу новостей
URL = "https://ria.ru/services/politics/more.html"

# Сегодняшний день
today = str(datetime.date.today())

# Преобразуем сегодняшний день для выполнения запроса
date = "".join(today.split("-"))

par = {
    "id": "1869469542",
    "date": date
}

head = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,ru;q=0.8,af;q=0.7"
}

# Ключевые слова
keywords = ["США", "Сочи"]


class HttpResponse:
    def get_response(self, url, params=None, headers=None):
        response = requests.request(
            method="GET",
            url=url,
            params=params,
            headers=headers
        )
        return self.check_response(response)

    def check_response(self, response: requests.Response):
        if response.status_code == 200:
            return response
        else:
            error_message = f"Your request returned {response.status_code} status code."
            if response.status_code == 404:
                error_message += " The requested resource wasn't found."
            elif response.status_code == 500:
                error_message += " The server encountered an internal error."
            raise Exception(error_message)


class NewsParser:
    def __init__(self):
        # self.today = str(date)
        self.http_response = HttpResponse()

    def get_html_page(self,
                      article_url: str,
                      params: Dict[str, Any] = None,
                      headers: Dict[str, Any] = None
                      ) -> BeautifulSoup:
        response = self.http_response.get_response(article_url, params, headers)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    def get_pages(self, soup: BeautifulSoup) -> List[str]:
        pages = []
        links = soup.find_all("a", {"class": "list-item__title"})
        for href in links:
            pages.append(href.get("href"))
        return pages

    def extract_info(self, article_url: str) -> Dict[str, Any] | None:
        soup = self.get_html_page(article_url, headers=head)

        title = soup.find(["div", "h1"], attrs={"class": "article__title"}).text

        summary = ' '.join([i.text for i in soup.findAll("div", class_="article__text")])
        first_sentence_pattern = r"^([^.]\D+[^.]+\.\s)"
        summary = re.sub(first_sentence_pattern, "", summary)

        if any(keyword in title for keyword in keywords) or any(keyword in summary for keyword in keywords):
            authors = soup.find("div", {"class": "endless__item"})["data-author"]
            return {"title": title, "summary": summary, "author": authors}
        else:
            return None

    def return_info(self, url, params, headers):
        soup = self.get_html_page(article_url=url, params=params, headers=headers)
        pages = self.get_pages(soup)

        result = []
        for page in pages:
            article_info = self.extract_info(page)
            if article_info:
                result.append(article_info)
        return result

    def run_for_the_day(self) -> List:
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)

        # +07:00 - часовой пояс Томска
        date_str = yesterday.strftime("%Y-%m-%dT%H:%M:%S+07:00")

        url = f"https://ria.ru/search/"

        # параметры запроса
        params = {
            "query": "",
            "tags": "",
            "dateFrom": date_str,
            "dateTo": date_str,
            "sort": 'relevance',
        }

        articles = self.return_info(url, params=params, headers=head)
        return articles

    def save_to_json(self, result: List[Dict[str, Any]]):
        with open("results.json", "w", encoding="utf-8") as outfile:
            json.dump(result, outfile, indent=4, ensure_ascii=False)

    def main(self):
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)

        # +07:00 - часовой пояс Томска
        date_str = yesterday.strftime("%Y-%m-%dT%H:%M:%S+07:00")

        url = f"https://ria.ru/search/"
        params = {
            "query": "",
            "tags": "",
            "dateFrom": date_str,
            "dateTo": date_str,
            "sort": 'relevance',
        }

        while True:
            now = datetime.datetime.now()
            print(f"Начало парсинга новостей: {now}")
            news = self.return_info(url=url, params=params, headers=head)
            print(f"Кол-во новостей: {len(news)}")
            for i in news:
                print(i["title"])
            # time.sleep(86400)
            time.sleep(1800)
            print()


if __name__ == "__main__":
    ria = NewsParser()
    ria.main()
