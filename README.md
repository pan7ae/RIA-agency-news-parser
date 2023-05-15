# Парсинг новостей с сайта информационного агентства (РИА Новости)
Этот скрипт предназначен для извлечения новостей с сайта новостного агентства с помощью Python и модулей `requests` и `bs4`. Скрипт автоматически определит и загрузит все статьи, опубликованные в течение 24 часов и содержащие упоминания о Республиканской и Демократической партиях США или о других темах на усмотрение пользователя.

В качестве целевого сайта использовалось новостное агенство [**РИА Новости**](https://ria.ru/).

## Требования
- Python 3.x;
- Библиотеки (модули):
  - [`requests`](https://requests.readthedocs.io/en/latest/);
  - [`BeautifulSoup4`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).
  - [`time`](https://docs.python.org/3/library/time.html);
  - [`datetime`](https://docs.python.org/3/library/datetime.html?highlight=datetime#module-datetime);
  - [`typing`](https://docs.python.org/3/library/typing.html?highlight=typing#module-typing);
  - [`json`](https://docs.python.org/3/library/json.html?highlight=json#module-json);
  - [`re`](https://docs.python.org/3/library/re.html?highlight=re#module-re).

## Как использовать
1. Клонируйте этот репозиторий или скачайте файл [`news_parser.py`](`news_parser.py`);
2. Установите необходимые модули с помощью ```pip install -r requirements.txt```;
3. Измените список ключевых слов в скрипте, чтобы выбрать интересные для Вас темы;
4. Запустите приложение с помощью ```python news_parser.py```;
5. Приложение автоматически сохранит все извлеченные статьи в JSON-файл под названием `articles.json`.

## Описание скрипта
- ### Импорт необходимых модулей
```python
import requests
from bs4 import BeautifulSoup
import time
import datetime
from typing import List, Dict, Any
import json
import re
```

- ### Headers для выполнения запроса (для предотвращения статус-кода 403)
```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 "
                  "Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,ru;q=0.8,af;q=0.7"
}
```

- ### Ключевые слова
```python
keywords = ["США", "Сочи"]
```

- ### HttpResponse. Класс отправки запроса на по URL-адресу
```python
class HttpResponse:
    def get_response(self, url, params=None, headers=None):
        """
        Выполняем запрос по ссылке
        """
        response = requests.request(
            method="GET",
            url=url,
            params=params,
            headers=headers
        )
        return self.check_response(response)

    def check_response(self, response: requests.Response):
        """
        Проверка статуса запроса
        """
        if response.status_code == 200:
            return response
        else:
            error_message = f"Your request returned {response.status_code} status code."
            if response.status_code == 404:
                error_message += " The requested resource wasn't found."
            elif response.status_code == 500:
                error_message += " The server encountered an internal error."
            raise Exception(error_message)
```

- ### NewsParser. Класс для парсинга страницы с новостями
```python
class NewsParser:
    def __init__(self):
        self.http_response = HttpResponse()

    def get_html_page(self,
                      article_url: str,
                      params: Dict[str, Any] = None,
                      headers: Dict[str, Any] = None
                      ) -> BeautifulSoup:
        """
        Получение HTML кода страницы
        """
        response = self.http_response.get_response(article_url, params, headers)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    def get_pages(self, soup: BeautifulSoup) -> List[str]:
        """
        Возвращаем список страниц с новостями
        """
        pages = []
        links = soup.find_all("a", {"class": "list-item__title"})
        for href in links:
            pages.append(href.get("href"))
        return pages

    def extract_info(self, article_url: str) -> Dict[str, Any] | None:
        """
        Извлечение необходимой информации с каждой новости
        """
        soup = self.get_html_page(article_url, headers=HEADERS)
        if soup.find(["div", "h1"], attrs={"class": "article__title"}):
            title = soup.find(["div", "h1"], attrs={"class": "article__title"}).text
        else:
            return None

        summary = ' '.join([i.text for i in soup.findAll("div", class_="article__text")])
        first_sentence_pattern = r"^([^.]\D+[^.]+\.\s)"
        summary = re.sub(first_sentence_pattern, "", summary)

        if any(keyword in title for keyword in keywords) or any(keyword in summary for keyword in keywords):
            authors = soup.find("div", {"class": "endless__item"})["data-author"]
            return {"title": title, "summary": summary, "author": authors}
        else:
            return None

    def return_info(self, url, params, headers):
        """
        Возврат новостей в списке и в JSON файле
        """
        soup = self.get_html_page(article_url=url, params=params, headers=headers)
        pages = self.get_pages(soup)

        # Открытие существующего JSON файла, иначе создание списка data
        try:
            data = self.read_json()
        except FileNotFoundError as e:
            data = []

        # На всякий случай создаем отдельный список, не связанный с data
        result = []

        for page in pages:
            article_info = self.extract_info(page)
            if article_info and article_info not in result and article_info not in data:
                data.append(article_info)
                result.append(article_info)
                self.save_to_json(data)
        return result

    def save_to_json(self, result: List[Dict[str, Any]]):
        """
        Сохранение/обновление JSON файла
        """
        with open("results.json", "w", encoding="utf-8") as outfile:
            json.dump(result, outfile, indent=4, ensure_ascii=False)

    def read_json(self) -> List[Dict[str, Any]]:
        """
        Чтение JSON файла
        """
        with open("results.json", "r", encoding="utf-8") as outfile:
            data = json.load(outfile)
        return data

    def main(self):
        """
        Основной блок программы
        """
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)

        # +07:00 - часовой пояс Томска
        date_str = yesterday.strftime("%Y-%m-%dT%H:%M:%S+07:00")

        # Основная ссылка
        url = f"https://ria.ru/search/"

        # params запроса
        params = {
            "query": "",
            "tags": "",
            "dateFrom": date_str,
            "dateTo": date_str,
            "sort": 'relevance',
        }

        # Бесконечный цикл
        while True:
            now = datetime.datetime.now()
            print(f"Начало парсинга новостей: {now}")
            news = self.return_info(url=url, params=params, headers=HEADERS)
            print(f"Кол-во новостей: {len(news)}")
            for i in news:
                print(i["title"])
            # time.sleep(86400)  # Запуск на сутки
            time.sleep(15)  # Запуск на более короткое время для проверки работы программы
            print()
```
