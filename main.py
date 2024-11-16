import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from get_new_lot import data_mining

API_TOKEN = '7558537384:AAEXdJ8FlS8Pd5h6CKKq_xs1AgfwNysv8oA'  # O'zingizning bot tokeningizni kiriting
USER_ID = '7131777042'  # Foydalanuvchi ID sini kiriting

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def send_periodic_message():
    while True:
        link_list, delta = await data_mining()
        if delta != 0:
            text = 'Lotlar linki: \n\n'
            for i in link_list:
                text += i + "\n"
            text += f"\nOxirgi 2 soat ichida {delta} ta yangi lot qo'shildi"
            await bot.send_message(USER_ID, text)
        else:
            await bot.send_message(USER_ID, text=f"Oxirgi 2 soat ichida {delta} yangi lot qo'shildi ammo ular bizga "
                                                 f"tegishli emas. Xatolik tufayli bizga tegishlisini ko'rmay qolgan "
                                                 f"bo'lishim mumkin, o'zingiz tekshirib Adminga xabar qiling, raxmat")

        await asyncio.sleep(2*60*60)


@dp.message_handler(commands='start_the_lott')
async def start_command(message: types.Message):
    await message.reply("Bot ishga tushdi va har 2 soatda xabar yuboradi.")
    if str(message.from_user.id) == "7131777042":
        await send_periodic_message()


@dp.message_handler(commands='start')
async def start_command(message: types.Message):
    await message.reply("Bot ishga tushdi va har 2 soatda xabar yuboradi.")


if __name__ == '__main__':
    executor.start_polling(dp)
