import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from get_new_lot import data_mining

API_TOKEN = '7558537384:AAEXdJ8FlS8Pd5h6CKKq_xs1AgfwNysv8oA'  # O'zingizning bot tokeningizni kiriting
USER_ID = '7131777042'  # Foydalanuvchi ID sini kiriting

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def send_periodic_message():
    print("ffuccc")
    while True:
        link_list = data_mining()
        if link_list:
            text = 'Lotlar linki: \n\n'
            for i in link_list:
                text += i + "\n"
            await bot.send_message(USER_ID, text)
        await asyncio.sleep(7200)


@dp.message_handler(commands='start_the_lott')
async def start_command(message: types.Message):
    if str(message.from_user.id) == "7131777042":
        await send_periodic_message()
    await message.reply("Bot ishga tushdi va har 2 soatda xabar yuboradi.")


@dp.message_handler(commands='start')
async def start_command(message: types.Message):
    await message.reply("Bot ishga tushdi va har 2 soatda xabar yuboradi.")


if __name__ == '__main__':
    executor.start_polling(dp)
