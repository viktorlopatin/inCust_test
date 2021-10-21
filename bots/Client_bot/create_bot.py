import asyncio
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN

loop = asyncio.get_event_loop()
storage = MemoryStorage()

bot = Bot(TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage, loop=loop)