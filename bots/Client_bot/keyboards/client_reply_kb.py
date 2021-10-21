from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

reply_keyboars_list = {}

#Клавиатура для команды /start
kb_start = ReplyKeyboardMarkup(resize_keyboard = True)
b1 = KeyboardButton("Каталог" )
b2 = KeyboardButton("Добавить событие")
kb_start.add(b1).add(b2)
reply_keyboars_list["start"] = kb_start


#Клавиатура для отмены создания события
kb_cencel = ReplyKeyboardMarkup(resize_keyboard = True)
b1 = KeyboardButton("❌ Отменить операцию")
kb_cencel.add(b1)
reply_keyboars_list["cencel_event"] = kb_cencel

#Клавиатура для выхода из кататлога
kb_main_menu = ReplyKeyboardMarkup(resize_keyboard = True)
b1 = KeyboardButton("+1")
b2 = KeyboardButton("+5")
b3 = KeyboardButton("Главное меню")
kb_main_menu.row(b1, b2).add(b3)
reply_keyboars_list["main_menu"] = kb_main_menu

#Клавиатура для выхода из кататлога
kb_cencel_chat = ReplyKeyboardMarkup(resize_keyboard = True)
b1 = KeyboardButton("❌Выйти из чата")
b2 = KeyboardButton("Посмотреть событие")
kb_cencel_chat.row(b1, b2)
reply_keyboars_list["cencel_chat"] = kb_cencel_chat