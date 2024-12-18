from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import exceptions as ex

from ...config import dp
from ...src.database.database import cursor, conn

router: Router = Router()


@router.message(F.text == "Toyifalar")
async def categories(message: Message):
    user_id = message.from_user.id
    # categories = cursor.execute("SELECT id, name FROM categories").fetchall()
    # button = []
    category_status = cursor.execute("""SELECT category_id FROM user_category WHERE user_id = ? AND status = ?""",
                                     (user_id, True)).fetchall()
    status_list = [status[0] for status in category_status]
    button_dict = {40: 'Продукты питания', 41: 'Бумага', 42: 'Канцелярские товары', 43: 'Мебель и офисное оборудование',
                   44: 'Одежда, обувь и постельные принадлежности',
                   46: 'Компьютерное оборудование, аудио-видео техника, информационные технологии и принадлежности',
                   47: 'Прочая техника и оборудование', 48: 'ТМЗ', 49: 'Услуги', 50: 'Ремонт', 51: 'Аренда',
                   52: 'Основные средства', 53: 'ГСМ', 54: 'Запасные части для транспортных средств',
                   55: 'Музыкальные инструменты', 56: 'Спортивный инвентарь и оборудования',
                   57: 'Минеральное удобрение', 58: 'Животные', 59: 'Цветы и растения',
                   60: 'Протезно-ортопедические изделия и технические средства реабилитации',
                   61: 'Лабораторные приборы, оборудования и техника', 62: 'Пестициды и Гербициды',
                   63: 'Протезно ортопедическое сырьё для стоматологии', 64: 'Звукозаписывающая техника и оборудование',
                   65: 'Обязательные платежи', 66: 'Содержание и ремонт компьютера и компьютерного оборудования',
                   67: 'Программный продукт', 68: 'Радиосвязное  оборудование и комплектующие',
                   70: 'Ветеринарные препараты, материалы, инструменты и оборудования',
                   71: 'Трубы и фитинги из термопластов', 72: 'Медикаменты', 73: 'Изделия медицинского назначения',
                   74: 'Медицинская техника и оборудование', 76: 'Биологически активные добавки'}
    builder = InlineKeyboardBuilder()
    for index, (key, value) in enumerate(button_dict.items()):
        if key in status_list:
            builder.button(text="✅" + value, callback_data=CategoryCallback(category_id=key).pack())
        else:
            builder.button(text=value, callback_data=CategoryCallback(category_id=key).pack())
        if (index + 1) % 2 == 0:
            builder.row()
    builder.adjust(2)
    activate = cursor.execute("""SELECT status FROM request WHERE user_id = ?""", (user_id,)).fetchone()
    if activate is None or activate[0] == '0':
        builder.button(text="☑️Faqat faollar", callback_data="faollar")
        builder.adjust(2)
    else:
        builder.button(text="✅Faqat faollar", callback_data="faollar")
        builder.adjust(2)
    # button = InlineKeyboardBuilder(markup=button)

    await message.answer(text="Quidagi toyifalardan o'zingizga keragini belgilab olishingiz mumkin",
                         reply_markup=builder.as_markup())


class CategoryCallback(CallbackData, prefix="category"):
    category_id: int


@dp.callback_query(CategoryCallback.filter())
async def handle_category_callback(callback: CallbackQuery, callback_data: CategoryCallback):
    try: await callback.answer()
    except ex.TelegramBadRequest: pass
    user_id = callback.from_user.id
    category_id = callback_data.category_id

    user_category = cursor.execute("""SELECT * FROM user_category WHERE user_id = ? AND category_id = ?""",
                                   (user_id, category_id)).fetchone()
    if user_category is None:
        cursor.execute("""INSERT INTO user_category (user_id, category_id, status) VALUES (?, ?, ?)""",
                       (user_id, category_id, True))
        conn.commit()
    else:
        if user_category[2]:
            cursor.execute("""UPDATE user_category SET status = ? WHERE user_id = ? AND category_id = ?""",
                           (False, user_id, category_id))
            conn.commit()
        else:
            cursor.execute("""UPDATE user_category SET status = ? WHERE user_id = ? AND category_id = ?""",
                           (True, user_id, category_id))
            conn.commit()
    category_status = cursor.execute("""SELECT category_id FROM user_category WHERE user_id = ? AND status = ?""",
                                     (user_id, True)).fetchall()
    status_list = [status[0] for status in category_status]
    button_dict = {40: 'Продукты питания', 41: 'Бумага', 42: 'Канцелярские товары', 43: 'Мебель и офисное оборудование',
                   44: 'Одежда, обувь и постельные принадлежности',
                   46: 'Компьютерное оборудование, аудио-видео техника, информационные технологии и принадлежности',
                   47: 'Прочая техника и оборудование', 48: 'ТМЗ', 49: 'Услуги', 50: 'Ремонт', 51: 'Аренда',
                   52: 'Основные средства', 53: 'ГСМ', 54: 'Запасные части для транспортных средств',
                   55: 'Музыкальные инструменты', 56: 'Спортивный инвентарь и оборудования',
                   57: 'Минеральное удобрение', 58: 'Животные', 59: 'Цветы и растения',
                   60: 'Протезно-ортопедические изделия и технические средства реабилитации',
                   61: 'Лабораторные приборы, оборудования и техника', 62: 'Пестициды и Гербициды',
                   63: 'Протезно ортопедическое сырьё для стоматологии', 64: 'Звукозаписывающая техника и оборудование',
                   65: 'Обязательные платежи', 66: 'Содержание и ремонт компьютера и компьютерного оборудования',
                   67: 'Программный продукт', 68: 'Радиосвязное  оборудование и комплектующие',
                   70: 'Ветеринарные препараты, материалы, инструменты и оборудования',
                   71: 'Трубы и фитинги из термопластов', 72: 'Медикаменты', 73: 'Изделия медицинского назначения',
                   74: 'Медицинская техника и оборудование', 76: 'Биологически активные добавки'}
    builder = InlineKeyboardBuilder()
    for index, (key, value) in enumerate(button_dict.items()):
        if key in status_list:
            builder.button(text="✅"+value, callback_data=CategoryCallback(category_id=key).pack())
            builder.adjust(2)
        else:
            builder.button(text=value, callback_data=CategoryCallback(category_id=key).pack())
            builder.adjust(2)
        if (index + 1) % 2 == 0:
            builder.row()
    activate = cursor.execute("""SELECT status FROM request WHERE user_id = ?""", (user_id, )).fetchone()
    if activate is None or activate[0] == '0':
        builder.button(text="☑️Faqat faollar", callback_data="faollar")
        builder.adjust(2)
    else:
        builder.button(text="✅Faqat faollar", callback_data="faollar")
        builder.adjust(2)

    try:
        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    except ex.TelegramBadRequest:
        pass


@dp.callback_query(lambda callback: callback.data.startswith("faollar"))
async def handle_category_callback(callback: CallbackQuery):
    if callback.data == "faollar":
        try: await callback.answer()
        except ex.TelegramBadRequest: pass
        user_id = callback.from_user.id

        category_status = cursor.execute("""SELECT category_id FROM user_category WHERE user_id = ? AND status = ?""",
                                         (user_id, True)).fetchall()
        status_list = [status[0] for status in category_status]
        button_dict = {40: 'Продукты питания', 41: 'Бумага', 42: 'Канцелярские товары', 43: 'Мебель и офисное оборудование',
                       44: 'Одежда, обувь и постельные принадлежности',
                       46: 'Компьютерное оборудование, аудио-видео техника, информационные технологии и принадлежности',
                       47: 'Прочая техника и оборудование', 48: 'ТМЗ', 49: 'Услуги', 50: 'Ремонт', 51: 'Аренда',
                       52: 'Основные средства', 53: 'ГСМ', 54: 'Запасные части для транспортных средств',
                       55: 'Музыкальные инструменты', 56: 'Спортивный инвентарь и оборудования',
                       57: 'Минеральное удобрение', 58: 'Животные', 59: 'Цветы и растения',
                       60: 'Протезно-ортопедические изделия и технические средства реабилитации',
                       61: 'Лабораторные приборы, оборудования и техника', 62: 'Пестициды и Гербициды',
                       63: 'Протезно ортопедическое сырьё для стоматологии', 64: 'Звукозаписывающая техника и оборудование',
                       65: 'Обязательные платежи', 66: 'Содержание и ремонт компьютера и компьютерного оборудования',
                       67: 'Программный продукт', 68: 'Радиосвязное  оборудование и комплектующие',
                       70: 'Ветеринарные препараты, материалы, инструменты и оборудования',
                       71: 'Трубы и фитинги из термопластов', 72: 'Медикаменты', 73: 'Изделия медицинского назначения',
                       74: 'Медицинская техника и оборудование', 76: 'Биологически активные добавки'}
        builder = InlineKeyboardBuilder()
        for index, (key, value) in enumerate(button_dict.items()):
            if key in status_list:
                builder.button(text="✅" + value, callback_data=CategoryCallback(category_id=key).pack())
            else:
                builder.button(text=value, callback_data=CategoryCallback(category_id=key).pack())
            if (index + 1) % 2 == 0:
                builder.row()

        activate = cursor.execute("""SELECT status FROM request WHERE user_id = ?""", (user_id,)).fetchone()
        if activate is None:
            cursor.execute("""INSERT INTO request (user_id, status) VALUES (?, ?)""", (user_id, True))
            conn.commit()
            act_status = True
        else:
            if activate[0] == "0":
                cursor.execute("""UPDATE request SET status = ? WHERE user_id = ?""", (True, user_id))
                conn.commit()
                act_status = True
            else:
                cursor.execute("""UPDATE request SET status = ? WHERE user_id = ?""", (False, user_id))
                conn.commit()
                act_status = False
        if act_status:
            builder.button(text="✅Faqat faollar", callback_data="faollar")
            builder.adjust(2)
        else:
            builder.button(text="☑️Faqat faollar", callback_data="faollar")
            builder.adjust(2)
        try:
            await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
        except ex.TelegramBadRequest:
            pass
