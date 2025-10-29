from aiogram import types
from aiogram.filters.command import Command
from database.db import get_result

async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    last = await get_result(user_id)
    if last is None:
        await message.answer("У вас ещё нет сохранённых результатов.")
    else:
        await message.answer(f"Ваш последний результат: {last} правильных ответов.")
