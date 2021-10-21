from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

reply_keyboars_list = {}


#Клавиатура для выхода из кататлога
kb_cencel_chat = ReplyKeyboardMarkup(resize_keyboard = True)
b1 = KeyboardButton("❌Выйти из чата")
kb_cencel_chat.add(b1)
reply_keyboars_list["cencel_chat"] = kb_cencel_chat