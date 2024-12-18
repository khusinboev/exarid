from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


from pathlib import Path

BASE_DIR = str(Path(__file__).resolve().parent)
DB_NAME = BASE_DIR + '/exarid.db'

TOKEN = "7558537384:AAGz5A8zmYezqW9EojMLCzRiyqwDzU8WCi4"
USER_ID = '7131777042'
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
