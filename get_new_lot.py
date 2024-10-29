import requests, lxml
from bs4 import BeautifulSoup


def get_last():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.121 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        # Boshqa kerakli headerslarni qo'shing
    }
    last_url = "https://exarid.uzex.uz/ru/bestoffer#"
    res = requests.get(url=last_url, headers=headers, verify=False).text
    soup = BeautifulSoup(res, features='lxml')
    last_lot = soup.find('a', class_="table_link").text.strip()
    return last_lot


def get_delta():
    new = int(get_last())
    with open('old_lot_number.py', 'r') as file:
        content = file.read()
    if content:
        old = int(content)
        delta = new - old + 1
        with open('old_lot_number.py', 'w') as file:
            file.write(str(new))
    else:
        with open('old_lot_number.py', 'w') as file:
            file.write(str(new))
        delta = 1
    return delta


def get_ex_urls():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.121 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }
    delta = get_delta()
    url = f"http://exarid.uzex.uz/ru/ajax/filter?page=1&PageSize={delta}&Type=BestOffer"
    res = requests.get(url=url, headers=headers, verify=False).text
    soup = BeautifulSoup(res, features='lxml')
    ex_urls = soup.find_all('a', class_="table_link", href=True)
    urls_list = []
    for i in ex_urls:
        urls_list.append("https://exarid.uzex.uz"+i['href'])
    return urls_list, delta


def data_mining():
    urls_list, delta = get_ex_urls()
    key_words = ["ТРЕНАЖЁР", "пневматический", "тир", "СТРЕЛКОВЫЙ ТРЕНАЖЁР", "ПКСТ", "ПКСТнинг", "Ўқ отиш", "тренажёрини", "Ўқ", "отиш", "тренажерный"]
    mining_url = []
    status = False
    for url in urls_list:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.121 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest'
        }
        res = requests.get(url=url, headers=headers, verify=False).text
        soup = BeautifulSoup(res, features='lxml')
        blocks = soup.find_all("div", class_="full_block content")
        for block in blocks:
            desc = block.find('p').t.text.strip()
            for key_word in key_words:
                if str(key_word).lower() in str(desc).lower():
                    status = True
                    break
            if status is True:
                mining_url.append(url)
                break

    return mining_url, delta
