from create_bot import bot, dp
from aiogram import types, Dispatcher
from keyboards import reply_keyboars_list
from handlers.catalog import send_message_with_media
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
	
	if len(message.text) == 6:
		current_state = await state.get_state()
		if current_state:
			await state.finish()

		await message.answer("Добро пожаловать, " + message["from"].first_name , reply_markup=reply_keyboars_list["start"])

	elif len(message.text) > 6:
		event = await db.getEvent(int(message.text[7:]))
		await send_message_with_media(message, event, False)

def register_handlers(dp: Dispatcher):
	dp.register_message_handler(start_handler, commands=["start"], state="*")

	