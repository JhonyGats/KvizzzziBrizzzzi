import asyncio, logging
import nest_asyncio
nest_asyncio.apply()

from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from aiogram import F
from config import API_TOKEN
from database.db import create_tables
from handlers.start import cmd_start
from handlers.stats import cmd_stats
from handlers.quiz import start_quiz, handle_answer

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Определяем хэдлеры
dp.message.register(cmd_start, Command("start"))
dp.message.register(start_quiz, Command("quiz"))
dp.message.register(start_quiz, F.text=="Начать игру")
dp.message.register(cmd_stats, Command("stats"))

dp.callback_query.register(handle_answer, lambda c: c.data and c.data.startswith("answer:"))

async def main():
    await create_tables()
    print("Бот запущен. Убедитесь, что в config.py указан ваш токен.")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
