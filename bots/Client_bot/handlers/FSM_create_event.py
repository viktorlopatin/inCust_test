from create_bot import bot, dp
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards import reply_keyboars_list

from database import *

#___Сострояние "Создать событие"___
class FSMCreateEvent(StatesGroup):
	nameEvent = State()
	title = State()
	description = State()
	media = State()
	endDate = State()

#Начало создания нового события
async def FSMCreateEventStart(message : types.Message):
	await FSMCreateEvent.nameEvent.set()
	await message.reply("Введите имя события:", reply_markup=reply_keyboars_list["cencel_event"])

#Получаем ответ от пользователя
async def FSMNameEvent(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data["nameEvent"] = message.text

	await FSMCreateEvent.next()
	await message.reply("Введите заголовок события\n(Можете использовать HTML разметку):")

#Получаем второй ответ от пользователя
async def FSMtitle(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data["title"] = message.text

	await FSMCreateEvent.next()
	await message.reply("Введите описание\n(Можете использовать HTML разметку):")

#Получаем третий ответ от пользователя
async def FSMdescription(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data["description"] = message.text

	await FSMCreateEvent.next()
	await message.reply("Пришлите медиа\n(Картинка, Анимация, Видео, Аудио):")

#Получаем 4 ответ от пользователя
async def FSMmedia(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		
		if message.photo:
			data["media"] = ("photo", message.photo[-1].file_id)
		elif message.video:
			data["media"] = ("video", message.video.file_id)
		elif message.animation:
			data["media"] = ("animation", message.animation.file_id)
		elif message.audio:
			data["media"] = ("audio", message.audio.file_id)


	await FSMCreateEvent.next()
	await message.reply("Дата окончания:")

#Получаем 5 ответ от пользователя
async def FSMendDate(message: types.Message, state: FSMContext):

	async with state.proxy() as data:
		data["endDate"] = message.text

	await db.addEvent(Event(message.chat.id, data["nameEvent"], data["title"], data["description"], data["media"][0], data["media"][1], data["endDate"]))

	text = data["title"] + "\n\n" + data["description"] + "\n\nВы создали событие👆👆👆\nДля того, чтобы получать уведомления о сообщениях перейдите в  @seervice_000_bot и напишите /start."
	if data["media"][0] == "photo": 
		await bot.send_photo(chat_id = message.chat.id, photo = data["media"][1], caption = text, reply_markup=reply_keyboars_list["start"])	
	elif data["media"][0] == "video": 
		await bot.send_video(chat_id = message.chat.id, video = data["media"][1], caption = text, reply_markup=reply_keyboars_list["start"])	
	elif data["media"][0] == "animation": 
		await bot.send_animation(chat_id = message.chat.id, animation = data["media"][1], caption = text, reply_markup=reply_keyboars_list["start"])	
	elif data["media"][0] == "audio": 
		await bot.send_audio(chat_id = message.chat.id, audio = data["media"][1], caption = text, reply_markup=reply_keyboars_list["start"])	

	
	await state.finish()
	


#Отменить создание события
async def cancel_handler(message: types.Message, state: FSMContext) :
	current_state = await state.get_state()
	if current_state is None:
		await message.reply("Создание события отменено", reply_markup=reply_keyboars_list["start"])
		return
		
	await state.finish()
	await message.reply("Создание события отменено", reply_markup=reply_keyboars_list["start"])

#___end___


def FSM_create_event_register_handlers(dp: Dispatcher):
	dp.register_message_handler(cancel_handler, filters.Text(equals="❌ Отменить операцию", ignore_case=True), state="*")
	dp.register_message_handler(FSMCreateEventStart, filters.Text(contains=["Добавить событие"], ignore_case=True), state=None)
	dp.register_message_handler(FSMNameEvent, state=FSMCreateEvent.nameEvent)
	dp.register_message_handler(FSMtitle, state=FSMCreateEvent.title)
	dp.register_message_handler(FSMdescription, state=FSMCreateEvent.description)
	dp.register_message_handler(FSMmedia, content_types=["photo", "video", "audio", "animation"], state=FSMCreateEvent.media)
	dp.register_message_handler(FSMendDate, state=FSMCreateEvent.endDate)