from create_bot import bot, dp
from keyboards import reply_keyboars_list
from database import *

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot
from config import SERVICE_BOT_TOKEN, TOKEN


from pprint import pprint

class FSMCatalog(StatesGroup):
	nameEvent = State()

class FSMchat(StatesGroup):
	chat = State()


async def send_message_with_media(message, event, with_button = True):
	if str(event.user_id) == str(message.chat.id):
		dutton_text = "Удалить"
		button_data = f"1.{str(event.id)}.{str(event.user_id)}.{str(message.chat.id)}"
	else:
		dutton_text = "Ответить"
		button_data = f"2.{str(event.id)}.{str(event.user_id)}.{str(message.chat.id)}"
	
	
	if with_button:
		inline_kb1 = InlineKeyboardMarkup().add(InlineKeyboardButton(dutton_text, callback_data=button_data))
	else:
		inline_kb1 = InlineKeyboardMarkup()

	text = event.title + "\n\n" + event.description
	if event.media_type == "photo": 
		await bot.send_photo(chat_id = message.chat.id, photo = event.media, caption = text, reply_markup=inline_kb1)	
	elif event.media_type == "video": 
		await bot.send_video(chat_id = message.chat.id, video = event.media, caption = text, reply_markup=inline_kb1)	
	elif event.media_type == "animation": 
		await bot.send_animation(chat_id = message.chat.id, animation = event.media, caption = text, reply_markup=inline_kb1)	
	elif event.media_type == "audio": 
		await bot.send_audio(chat_id = message.chat.id, audio = event.media, caption = text, reply_markup=inline_kb1)


async def catalog_handler(message : types.Message, state: FSMCatalog):
	user = await db.getUser(message.chat.id)
	if user == None:
		await message.answer("Введите команду /start")
		return


	await FSMCatalog.nameEvent.set()
	data_events = await db.getEvents()

	async with state.proxy() as data:
		data["events"] = data_events


	await message.answer("Каталог:", reply_markup=reply_keyboars_list["main_menu"])

	if_send = False
	for x in range(2):
		if x < len(data["events"]):
			await send_message_with_media(message, data["events"][x])
			async with state.proxy() as data:
				data["iter"] = 2
			if_send = True

	if if_send == False:
		await message.answer("Событий нет")
	

async def catalog_handler_2_or_5(message : types.Message, state: FSMCatalog.nameEvent):
	user = await db.getUser(message.chat.id)
	if user == None:
		await message.answer("Введите команду /start")
		return

	if_send = False
	async with state.proxy() as data:
		if "iter" in data:
			for x in range(int(message.text[1:])):
				if x + data["iter"] < len(data["events"]):
					await send_message_with_media(message, data["events"][x + data["iter"]])
					if_send = True

		

	if if_send == False:
		await message.answer("Событий больше нет")


	
#Отменить создание события
async def cancel_catalog(message: types.Message, state: FSMCatalog) :
	current_state = await state.get_state()
	if current_state is None:
		await message.answer("Вы вернулись в главное меню", reply_markup=reply_keyboars_list["start"])
		return
		
	await state.finish()
	await message.answer("Вы вернулись в главное меню", reply_markup=reply_keyboars_list["start"])

#Удалить событие (проверка на дурака)
async def delete_event_check(callback_query: types.CallbackQuery):
	text = "Вы уверенны что хотите удалить данное событие?"
	callback_data = str(callback_query.message.reply_markup.inline_keyboard[0][0].callback_data)
	
	
	inline_kb = InlineKeyboardMarkup().row(
		InlineKeyboardButton("Да", callback_data=str(3) + callback_data[1:]),
		InlineKeyboardButton("Нет", callback_data=str(4) + callback_data[1:]))
	await callback_query.message.reply(text, reply_markup=inline_kb)

#Отменить удаление события
async def delete_event_cencel(callback_query: types.CallbackQuery):
	await callback_query.message.edit_text("Событие не было удалено")

#Улалить событие окончательно
async def delete_event(callback_query: types.CallbackQuery):
	event_id = str(callback_query.message.reply_markup.inline_keyboard[0][0].callback_data).split(".")[1]
	await db.delEvent(event_id)
	await callback_query.message.edit_text("Событие удалено")

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
	await callback_query.message.reply("Вы вошли в чат с владельцем события\nПоддерживаемый тип собщений:\n1. Текст", reply_markup=reply_keyboars_list["cencel_chat"])

#Отправить сообщение владельцу события
async def send_message_chat_hundler(message: types.Message, state: FSMchat.chat):

	async with state.proxy() as data:
		callback_data = data["callback_data"]

	
	with bot.with_token(SERVICE_BOT_TOKEN):
		if message.text:
			user = await db.getUser(message.chat.id)
			admin = await db.getUser(callback_data[2])
			event = await db.getEvent(callback_data[1])
			text = f"#Сообщение {event.title}\n{user.name}: {message.text}"

			if admin.with_chat != user.chat_id:
				inline_kb = InlineKeyboardMarkup()
				inline_kb.add(InlineKeyboardButton(f"Ответить {user.name}", callback_data=f"0.{event.id}.{user.chat_id}"))
				inline_kb.add(InlineKeyboardButton("Посмотреть событие", url="t.me/client_0000_bot?start=" + str(callback_data[1])))
				await bot.send_message(callback_data[2], text, entities=message.entities, reply_markup=inline_kb)
			else:
				await bot.send_message(callback_data[2], text, entities=message.entities)

		#await bot.send_message(callback_data[2], str(message))

	#await message.reply(message.text)

#Выйти из чата с владельцем события
async def cancel_chat_hundler(message: types.Message, state: FSMchat.chat) :
	current_state = await state.get_state()
	if current_state is None:
		await message.answer("Вы вышли из чата и вернулись в главное меню", reply_markup=reply_keyboars_list["start"])
		return

	user = await db.getUser(message.chat.id)
	user.with_chat = 0
	await db.commit()

	await state.finish()
	await message.answer("Вы вышли из чата и вернулись в главное меню", reply_markup=reply_keyboars_list["start"])

#Выйти из чата с владельцем события
async def show_event_hundler(message: types.Message, state: FSMchat.chat) :
	async with state.proxy() as data:
		callback_data = data["callback_data"]
	event = await db.getEvent(callback_data[1])
	await send_message_with_media(message, event, False)

#Показать соб
#async def cancel_chat_hundler(message: types.Message, state: FSMchat.chat) :	

def register_handlers_catalog(dp: Dispatcher):
	dp.register_message_handler(cancel_catalog, filters.Text(equals="Главное меню", ignore_case=True), state="*")
	dp.register_message_handler(catalog_handler, filters.Text(contains=["Каталог"], ignore_case=True), state=None)
	dp.register_message_handler(catalog_handler_2_or_5, filters.Text(startswith="+"), state=FSMCatalog.nameEvent)

	#Удалить событие (проверка на дурака)
	dp.register_callback_query_handler(delete_event_check, filters.Text(startswith="1"), state=FSMCatalog.nameEvent)
	#Отменить удаление события
	dp.register_callback_query_handler(delete_event_cencel, filters.Text(startswith="4"), state=FSMCatalog.nameEvent)
	#Отменить удаление события
	dp.register_callback_query_handler(delete_event, filters.Text(startswith="3"), state=FSMCatalog.nameEvent)

	dp.register_callback_query_handler(chat_hundler, filters.Text(startswith="2"), state=None)
	dp.register_callback_query_handler(chat_hundler, filters.Text(startswith="2"), state=FSMCatalog.nameEvent)

	dp.register_message_handler(show_event_hundler, filters.Text(contains=["Посмотреть событие"]), state=FSMchat.chat)
	dp.register_message_handler(cancel_chat_hundler, filters.Text(contains=["❌Выйти из чата"]), state=FSMchat.chat)
	dp.register_message_handler(send_message_chat_hundler, content_types=["text", "photo", "video", "audio", "animation"], state=FSMchat.chat)
	"""
	callback_data
	1 - Удалить событие(проверка на дурака)
	2 - Ответить на событие
	3 - Улалить событие окончательно
	4 - Отменить удаление события
	"""