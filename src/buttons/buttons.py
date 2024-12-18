from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_menu = ReplyKeyboardMarkup(resize_keyboard=True,
                                keyboard=[[KeyboardButton(text="Toyifalar"), KeyboardButton(text="Buyurtmachilar")],
                                          [KeyboardButton(text="❓So'rov yaratish")]])

customer = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="🛖Bosh bo'lim")]])

request_handle = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="🛖Bosh bo'lim")]])
