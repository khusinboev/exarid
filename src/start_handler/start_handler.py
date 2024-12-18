from aiogram import html, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from ...src.buttons.buttons import main_menu
from ...src.database.database import user_exists, add_user

router: Router = Router()


class Form(StatesGroup):
    signup = State()


@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    try: await state.clear()
    except: pass
    user_id = message.from_user.id
    if not user_exists(user_id):
        await message.answer("Ismingizni yuboring:")
        await state.set_state(Form.signup)
    else:
        await message.answer("Menu", reply_markup=main_menu)


@router.message(Form.signup)
async def echo_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    name = message.text
    add_user(user_id, name)
    await state.clear()
    await message.answer("Ro'yxatdan o'tdingiz! Endi menyudan foydalanishingiz mumkin.", reply_markup=main_menu)


@router.message(F.text == "🛖Bosh bo'lim")
async def echo_handler(message: Message, state: FSMContext) -> None:
    try: await state.clear()
    except: pass
    await message.answer("Menu", reply_markup=main_menu)
