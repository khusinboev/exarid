import sqlite3

import requests
import urllib3
from bs4 import BeautifulSoup

from ...config import DB_NAME
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()


def user_exists(user_id: int) -> bool:
    cursor.execute("SELECT 1 FROM user WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone() is not None
    return exists


def add_user(user_id: int, name: str):
    cursor.execute("INSERT INTO user (user_id, name) VALUES (?, ?)", (user_id, name))
    conn.commit()


def set_categories():
    urllib3.disable_warnings()
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
        value = int(i['value'].strip())
        cursor.execute("SELECT 1 FROM categories WHERE id = ? OR name = ?", (value, category))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO categories (id, name) VALUES (?, ?)", (value, category))
            conn.commit()


def create_table():
    # Jadval yaratish SQL buyruqlari

    # Har bir jadvalni yaratish
    table_creation_queries = [
        """
        CREATE TABLE IF NOT EXISTS user (
            user_id INTEGER UNIQUE,
            name TEXT NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER UNIQUE,
            name TEXT NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS request (
            user_id INTEGER,
            status TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS user_category (
            user_id INTEGER,
            category_id INTEGER,
            status BOOL NOT NULL,
            UNIQUE (user_id, category_id),
            FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS customers (
            user_id INTEGER,
            inn TEXT,
            name TEXT NOT NULL,
            UNIQUE (user_id, inn),
            FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE
        );
        """
        # """
        # CREATE TABLE IF NOT EXISTS customers (
        #     inn TEXT PRIMARY KEY,
        #     name TEXT NOT NULL
        # );
        # """,
        # """
        # CREATE TABLE IF NOT EXISTS user_customer (
        #     user_id INTEGER,
        #     customer_inn TEXT,
        #     status BOOL NOT NULL,
        #     PRIMARY KEY (user_id, customer_inn),
        #     FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE,
        #     FOREIGN KEY (customer_inn) REFERENCES customers (inn) ON DELETE CASCADE
        # );
        # """
    ]
    for query in table_creation_queries:
        cursor.execute(query)
        print("Table created successfully!")
    print("All tables created successfully in SQLite database!")
    set_categories()
    try:
        pass
    except Exception as e:
        print("An error occurred while creating tables:", e)
    finally:
        # Ulashlarni yopish
        conn.commit()
        cursor.close()
        conn.close()


# create_table()
