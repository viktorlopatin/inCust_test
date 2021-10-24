from create_bot import bot, dp
from aiogram import types, Dispatcher
from keyboards import reply_keyboars_list
from handlers.catalog import send_message_with_media
from aiogram.dispatcher import FSMContext, filters
from database import *


#Ответ на команду /start
async def start_handler(message : types.Message, state):
	user = await db.getUser(message.chat.id)
	if user == None:
		await db.addUser(User(message.chat.id, message["from"].first_name, message["from"].username, True, False, 0))
	else:
		if user.in_client_bot == False:
			user.in_client_bot = True
			
		user.with_chat = 0
		await db.commit()
	
	
	current_state = await state.get_state()
	if current_state:
		await state.finish()

	await message.answer("Добро пожаловать, " + message["from"].first_name , reply_markup=reply_keyboars_list["start"])

	

#Ответ на команду /start
async def start_handler_show_event(message : types.Message, state):
	user = await db.getUser(message.chat.id)

	reply_markup = None
	print(user.with_chat)
	if user.with_chat != 0:
		reply_markup = reply_keyboars_list["cencel_chat"]
	else:
		reply_markup = reply_keyboars_list["start"]

	event = await db.getEvent(int(message.text[7:]))
	await send_message_with_media(message, event, False, reply_markup)

def register_handlers(dp: Dispatcher):
	dp.register_message_handler(start_handler_show_event, filters.Text(startswith="/start "), state="*")
	dp.register_message_handler(start_handler, commands=["start"], state="*")

	