from aiogram import executor
from config import admin_id
from create_bot import bot, dp

from handlers import *


async def send_to_admin(dp):
	await bot.send_message(chat_id = admin_id, text = "Бот запущен")

if __name__ == "__main__":
	handlers_client.register_handlers(dp)
	executor.start_polling(dp, on_startup=send_to_admin)