import asyncio
import threading
import time
from datetime import datetime

import requests
import urllib3
import xlsxwriter
import pandas as pd
from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import exceptions as ex
from bs4 import BeautifulSoup

from ...config import dp, bot, BASE_DIR
from ...src.buttons.buttons import customer, main_menu, request_handle
from ...src.database.database import cursor, conn

router: Router = Router()
urllib3.disable_warnings()


class CreateRequest(StatesGroup):
    handle_request1 = State()
    handle_request2 = State()


@router.message(F.text == "❓So'rov yaratish")
async def handle_request1(message: Message, state: FSMContext):
    await message.answer("Bu bo'limda siz EXARID.UZEX.UZ saytidagi ma'lumotlardan nechtasini tortish kerakligini "
                         "yozib yuborishingiz kerak, ILTIMOS SON KIRITING va 5000dan kichik bo'lsin\n"
                         "Oxirgi 5000ta ma'lumot tahminan oxirgi 3 oyniki bo'ladi", reply_markup=request_handle)
    await state.set_state(CreateRequest.handle_request1)


@router.message(CreateRequest.handle_request1)
async def handle_request2(message: Message, state: FSMContext):
    if message.text == "🛖Bosh bo'lim":
        await state.clear()
        await message.answer(text="Bosh bo'lim", reply_markup=main_menu)
    elif message.text.isdigit() and int(message.text) <= 10000:
        await state.clear()
        await message.answer(text="Qabul qilindi, ma'lumotlar qayta ishlab bo'lingach sizga excellni yuboramiz",
                             reply_markup=main_menu)
        chat_id = message.from_user.id
        length = message.text
        category_ids = cursor.execute("SELECT category_id FROM user_category WHERE user_id = ? and status = ?",
                                      (chat_id, True)).fetchall()
        category_ids = [i[0] for i in category_ids]
        quest = ",".join("?" for _ in category_ids)
        category_names = [i[0] for i in cursor.execute(f"SELECT name FROM categories WHERE id IN ({quest})",
                                                       category_ids)]
        customer_inn = [i[0] for i in cursor.execute("SELECT inn FROM customers WHERE user_id = ?", (chat_id, )).fetchall()]

        task = threading.Thread(target=request_processing,
                                args=(category_ids, category_names, length, chat_id, customer_inn, ))
        task.start()

    else: await message.answer("Iltimos faqat son yuboring va 5000mingdan kichik bo'lsin. "
                               "\nOxirgi 5000ta ma'lumot tahminan oxirgi 3 oyniki bo'ladi")


def check_date(input_date):
    today = datetime.today()
    input_date = datetime.strptime(input_date, "%d.%m.%Y")
    return input_date >= today


def request_processing(category_ids, category_names, length, chat_id, customer_inn):
    activate = cursor.execute("""SELECT status FROM request WHERE user_id = ?""", (chat_id,)).fetchone()
    if activate and activate[0] == "1":
        activate = True
    else: activate = False
    filter_1 = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.121 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }
    url = f"https://exarid.uzex.uz/ru/ajax/filter?page=1&PageSize={length}&Type=BestOffer"
    res = requests.get(url=url, headers=headers, verify=False).text
    soup = BeautifulSoup(res, features='lxml')
    ex_urls = soup.find_all('a', class_="table_link", href=True)
    if category_names:
        for ex_url in ex_urls:
            if ex_url.text.strip() in category_names:
                filter_1.append("https://exarid.uzex.uz" + ex_url['href'])
    else:
        for ex_url in ex_urls:
            filter_1.append("https://exarid.uzex.uz" + ex_url['href'])
    filter_1 = list(set(filter_1))
    filter_2 = []
    if customer_inn:
        for fil1 in filter_1:
            res = requests.get(url=fil1, headers=headers, verify=False).text
            soup = BeautifulSoup(res, features='lxml')
            ex_urls = soup.find_all('div', class_="right_element")[1]
            if ex_urls.text.strip() in customer_inn:
                filter_2.append(fil1)
    else:
        for fil1 in filter_1:
            filter_2.append(fil1)

    if len(filter_2) > 0:
        excell_file = BASE_DIR + f'\\src\\files\\{chat_id}.xlsx'
        workbook = xlsxwriter.Workbook(excell_file)
        worksheet = workbook.add_worksheet()
        worksheet.write(0, 0, "Lot raqami")
        worksheet.write(0, 1, "Urls")
        worksheet.write(0, 2, "Tugash sanasi")
        worksheet.write(0, 3, "INN")
        worksheet.write(0, 4, "Buyurtmachi")
        worksheet.write(0, 5, "Tafsilot-1")
        row = 1
        if activate:
            for fil2 in filter_2:
                res = requests.get(url=fil2, headers=headers, verify=False).text
                soup = BeautifulSoup(res, features='lxml')
                end_date = str(soup.find_all('ul', class_="product_info")[0].find("div", class_="right_element table_text_red").text).strip()
                if check_date(end_date):
                    lot_number = fil2.split('/')[-1]
                    worksheet.write(row, 0, lot_number)
                    havola = fil2
                    worksheet.write(row, 1, havola)
                    print(end_date)
                    worksheet.write(row, 2, end_date)
                    inn = soup.find_all('div', class_="right_element")[1].text.strip()
                    worksheet.write(row, 3, inn)
                    customer_name = soup.find_all('div', class_="right_element")[0].text.strip()
                    worksheet.write(row, 4, customer_name)
                    get_full_block = soup.find(lambda tag: tag.name == "div" and "full_block" in tag.get("class", []) and len(tag.get("class", [])) == 1)
                    description = get_full_block.find_all("div", class_="content")[0].text.strip()
                    worksheet.write(row, 5, description)

                    min_titles = soup.find_all("h3", class_="min_title")
                    r = 0
                    for min_title in min_titles:
                        worksheet.write(0, 6+r, f"Tafsilot-{r+2}")
                        min_title = min_title.text.strip()
                        batafsil_datas = soup.find_all("div", class_="full_block content")[r].find("p").text.strip()
                        worksheet.write(row, 6+r, min_title + "\n" + batafsil_datas)
                        r += 1
                    row += 1
            else:
                for fil2 in filter_2:
                    res = requests.get(url=fil2, headers=headers, verify=False).text
                    soup = BeautifulSoup(res, features='lxml')
                    end_date = str(soup.find_all('ul', class_="product_info")[0].find("div", class_="right_element table_text_red").text).strip()
                    lot_number = fil2.split('/')[-1]
                    worksheet.write(row, 0, lot_number)
                    havola = fil2
                    worksheet.write(row, 1, havola)
                    print(end_date)
                    worksheet.write(row, 2, end_date)
                    inn = soup.find_all('div', class_="right_element")[1].text.strip()
                    worksheet.write(row, 3, inn)
                    customer_name = soup.find_all('div', class_="right_element")[0].text.strip()
                    worksheet.write(row, 4, customer_name)
                    get_full_block = soup.find(
                        lambda tag: tag.name == "div" and "full_block" in tag.get("class", []) and len(
                            tag.get("class", [])) == 1)
                    description = get_full_block.find_all("div", class_="content")[0].text.strip()
                    worksheet.write(row, 5, description)

                    min_titles = soup.find_all("h3", class_="min_title")
                    r = 0
                    for min_title in min_titles:
                        worksheet.write(0, 6 + r, f"Tafsilot-{r + 2}")
                        min_title = min_title.text.strip()
                        batafsil_datas = soup.find_all("div", class_="full_block content")[r].find("p").text.strip()
                        worksheet.write(row, 6 + r, min_title + "\n" + batafsil_datas)
                        r += 1
                    row += 1

        workbook.close()

        url = f"https://api.telegram.org/bot{bot.token}/sendDocument"

        with open(excell_file, "rb") as document:
            requests.post(
                url,
                data={"chat_id": chat_id},
                files={"document": (f"Oxirgi {length}ta elondan saralab olinganlar.xlsx", document)},
            )
        csv_file_path = f'{excell_file[:-4]}csv'
        excel_file2 = pd.read_excel(excell_file)
        excel_file2.to_csv(csv_file_path, index=False)
        with open(csv_file_path, "rb") as csv:
            requests.post(
                url,
                data={"chat_id": chat_id},
                files={"document": (f"Oxirgi {length}ta elondan saralab olinganlar.csv", csv)},
            )
    else:
        url = f"https://api.telegram.org/bot{bot.token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": "Berilgan ma'lumotlar bo'yicha elonlar topilmadi"
        }
        requests.post(url, json=payload)
