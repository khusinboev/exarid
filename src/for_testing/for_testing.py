import sqlite3
from time import time

import requests, lxml
from bs4 import BeautifulSoup

from ...config import DB_NAME

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()


def set_categories():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/112.0.5615.121 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
    }
    last_url = "https://exarid.uzex.uz/ru/bestoffer#"

    res = requests.get(url=last_url, headers=headers, verify=False).text
    soup = BeautifulSoup(res, features='lxml')
    data = soup.find('select', id="Filter_CategoryID")

    categories = data.find_all("option")[1:]
    for i in categories:
        category = i.text.strip()
        print(category)
        value = int(i['value'].strip())

        cursor.execute("INSERT INTO categories (id, name) VALUES (?, ?)", (value, category))
        conn.commit()
