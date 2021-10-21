from create_bot import bot, dp
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards import reply_keyboars_list
from config import CLIENT_BOT_TOKEN
from database import *

#Ответ на команду /start
async def start_handler(message : types.Message):
	user = await db.getUser(message.chat.id)
	if user == None:
		await db.addUser(User(message.chat.id, message["from"].first_name, message["from"].username, False, True, 0))
	else:
		if user.in_service_bot == False:
			user.in_service_bot = True

		user.with_chat = 0
		await db.commit()

	await message.answer("Добро пожаловать, " + message["from"].first_name)


class FSMchat(StatesGroup):
	chat = State()

#Запустить чат с владельцем события
async def chat_hundler(callback_query: types.CallbackQuery, state):
	current_state = await state.get_state()
	if current_state:
		await state.finish()
	
	callback_data = str(callback_query.message.reply_markup.inline_keyboard[0][0].callback_data).split(".")
	print(callback_data)
	await FSMchat.chat.set()
	
	async with state.proxy() as data:
		data["callback_data"] = callback_data

	user = await db.getUser(callback_query.message.chat.id)
	user.with_chat = callback_data[2]
	await db.commit()
	await callback_query.message.reply("Вы вошли в чат с пользователем\nПоддерживаемый тип собщений:\n1. Текст", reply_markup=reply_keyboars_list["cencel_chat"])

#Отправить сообщение пользователю
async def send_message_chat_hundler(message: types.Message, state: FSMchat.chat):

	async with state.proxy() as data:
		callback_data = data["callback_data"]

	
	with bot.with_token(CLIENT_BOT_TOKEN):
		if message.text:
			user = await db.getUser(message.chat.id)
			event = await db.getEvent(callback_data[1])
			

			text = f"#Сообщение {event.title}\n{user.name}: {message.text}"
			await bot.send_message(callback_data[2], text, entities=message.entities)

#Выйти из чата с пользователем
async def cancel_chat_hundler(message: types.Message, state: FSMchat.chat) :
	current_state = await state.get_state()
	if current_state is None:
		await message.answer("Вы вышли из чата", reply_markup=types.ReplyKeyboardRemove())
		return

	user = await db.getUser(message.chat.id)
	user.with_chat = 0
	await db.commit()

	await state.finish()
	await message.answer("Вы вышли из чата", reply_markup=types.ReplyKeyboardRemove())

def register_handlers(dp: Dispatcher):
	dp.register_callback_query_handler(chat_hundler, filters.Text(startswith="0"), state=None)
	dp.register_message_handler(cancel_chat_hundler, filters.Text(contains=["❌Выйти из чата"]), state=FSMchat.chat)
	dp.register_message_handler(send_message_chat_hundler, content_types=["text", "photo", "video", "audio", "animation"], state=FSMchat.chat)
	dp.register_message_handler(start_handler, commands=["start"])

	