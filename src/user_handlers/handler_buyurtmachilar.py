from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import exceptions as ex

from ...config import dp
from ...src.buttons.buttons import customer, main_menu
from ...src.database.database import cursor, conn

router: Router = Router()


class CustomerState(StatesGroup):
    customer1 = State()
    customer2 = State()


@router.message(F.text == "Buyurtmachilar")
async def handle_buyurtmachilar(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_customers = cursor.execute("SELECT inn, name FROM customers WHERE user_id = ?", (user_id, )).fetchall()
    if user_customers:
        result_text = f"Sizda hozirda <b>{len(user_customers)}</b>ta tashkilot qo'shilgan\n\n"
        for user_customer in user_customers:
            if len(str(user_customer[1]).split()) > 4:name_message = f"{' '.join(str(user_customer[1]).split()[:3])}..."
            else: name_message = user_customer[1]
            result_text += f"<code>{user_customer[0]}</code><i> - {name_message}</i>\n"

        result_text += ("\n\nYangi tashkilot qo'shish yoki mavjudini olib tashlash uchun uning <b>INN</b>sini yuboring."
                        " <i>Misol: 123456789</i>")
    else:
        result_text = "Hozirda hech qaysi tashkilotlar qo'shilmagan"
        result_text += ("\n\nYangi tashkilot qo'shish yoki mavjudini olib tashlash uchun uning <b>INN</b>sini yuboring."
                        " <i>Misol: 123456789</i>")

    await message.answer(text=result_text, parse_mode="HTML", reply_markup=customer)
    await state.set_state(CustomerState.customer1)


@router.message(CustomerState.customer1)
async def customer_state1(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    if message.text == "🛖Bosh bo'lim":
        await message.answer("🛖Bosh bo'lim", reply_markup=main_menu)
    else:
        user_customers = cursor.execute("SELECT inn, name FROM customers WHERE user_id = ? and inn = ?",
                                        (user_id, message.text)).fetchone()
        if user_customers:
            cursor.execute("DELETE FROM customers WHERE inn = ?", (message.text, ))
            conn.commit()
            await message.answer(f"Bu INN ga ega tashkilot bazadan o'chirib yuborildi\n\n"
                                 f"<code>{user_customers[0]}</code> - <i>{user_customers[1]}</i>",
                                 reply_markup=main_menu)
        else:
            await message.answer("Tashkilotning INN si qabul qilindi, endi tashkilot nomini yuboring")
            await state.set_state(CustomerState.customer2)
            await state.update_data(inn=message.text)


@router.message(CustomerState.customer2)
async def customer_state2(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "🛖Bosh bo'lim":
        await state.clear()
        await message.answer("🛖Bosh bo'lim", reply_markup=main_menu)
    else:
        inn = (await state.get_data()).get("inn")
        customer_name = message.text
        try:
            cursor.execute("INSERT INTO customers (user_id, inn, name) VALUES (?, ?, ?)", (user_id, inn, customer_name))
            conn.commit()
        except Exception as e:
            await message.answer(f"Xatolik: {e}\n\nImkon qadar dasturchiga xabar bering: @adkhambek_4")

        await message.answer(text="Tashkilot muvaffaqiyatli bazaga qo'shildi, Davom etishingiz mumkin",
                             reply_markup=main_menu)
        await state.clear()
